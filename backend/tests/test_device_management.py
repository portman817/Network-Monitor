from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from app import ping


def test_added_device_in_configured_subnet_is_checkable(client, monkeypatch):
    monkeypatch.setattr(ping, "ALLOWED_NETWORKS", ping.configured_networks("192.168.0.0/24"))
    for address, allowed in [("192.168.0.42", True), ("192.168.0.255", False),
                             ("192.168.1.42", False), ("router.local", False)]:
        response = client.post("/api/devices", json={"name": address, "address": address})
        assert response.status_code == 201
        assert response.json()["check_allowed"] is allowed
        if allowed:
            assert ping.allowed_target(address) == address


def test_public_network_cannot_be_configured():
    with pytest.raises(ValueError, match="private IPv4"):
        ping.configured_networks("0.0.0.0/0")


@pytest.mark.parametrize("address", ["8.8.8.8", "192.168.0.0/24", "::1", "router.local"])
def test_invalid_individual_permissions_are_rejected(address):
    with pytest.raises(ValueError):
        ping.configured_addresses(address)


def test_individual_permissions_are_independent_of_saved_devices(client, monkeypatch):
    monkeypatch.setattr(ping, "ALLOWED_NETWORKS", ())
    monkeypatch.setattr(ping, "ALLOWED_ADDRESSES", ping.configured_addresses(" 192.168.0.42 "))
    for address, allowed in [("192.168.0.42", True), ("192.168.0.247", False)]:
        device = client.post("/api/devices", json={"name": "Device", "address": address}).json()
        assert device["check_allowed"] is allowed
    assert ping.configured_addresses("") == frozenset()


def test_edit_preserves_measurement_on_rename_and_resets_it_on_address_change(client):
    device = client.post("/api/devices", json={"name": "Local", "address": "127.0.0.1"}).json()
    path = f"/api/devices/{device['id']}"
    client.app.state.ping_runner = lambda _: ping.PingResult("online", 0)
    checked = client.post(f"{path}/check").json()
    renamed = client.put(path, json={"name": "Renamed", "address": device["address"]})
    assert renamed.json() == {**checked, "name": "Renamed"}

    changed = client.put(path, json={"name": "Renamed", "address": "Router.Local."})
    assert changed.json() == {**device, "name": "Renamed", "address": "router.local", "check_allowed": False}
    assert client.get("/api/devices").json() == [changed.json()]
    assert device["id"] not in client.app.state.check_limiter.last_started


def test_edit_rejects_invalid_duplicate_and_missing_devices(client):
    device = client.post("/api/devices", json={"name": "Local", "address": "127.0.0.1"}).json()
    client.post("/api/devices", json={"name": "Router", "address": "router.local"})
    path = f"/api/devices/{device['id']}"
    assert client.put(path, json={"name": "New", "address": "999.999.999.999"}).status_code == 422
    payload = {"name": "New", "address": "Router.Local."}
    duplicate = client.put(path, json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "duplicate_address"
    assert client.get("/api/devices").json()[0] == device
    assert client.put("/api/devices/999", json=payload).status_code == 404


def test_delete_device(client):
    created = client.post("/api/devices", json={"name": "Test", "address": "127.0.0.1"})
    path = f"/api/devices/{created.json()['id']}"
    assert client.delete(path).status_code == 204
    assert client.get("/api/devices").json() == []
    assert client.delete(path).status_code == 404


def test_rejected_checks_do_not_start_cooldown(client):
    device = client.post("/api/devices", json={"name": "Router", "address": "router.local"}).json()
    client.app.state.ping_runner = lambda _: pytest.fail("Rejected request attempted Ping")
    for path, expected in [(f"/api/devices/{device['id']}/check", 403), ("/api/devices/999/check", 404)]:
        assert [client.post(path).status_code for _ in range(2)] == [expected, expected]
    assert not client.app.state.check_limiter.last_started


def test_delete_is_blocked_during_check(client):
    device = client.post("/api/devices", json={"name": "Local", "address": "127.0.0.1"}).json()
    path = f"/api/devices/{device['id']}"
    started, release = Event(), Event()

    def pending_ping(_):
        started.set()
        assert release.wait(5)
        return ping.PingResult("online", 0)

    client.app.state.ping_runner = pending_ping
    with ThreadPoolExecutor(max_workers=1) as executor:
        check = executor.submit(client.post, f"{path}/check")
        try:
            assert started.wait(5)
            response = client.delete(path)
            assert response.status_code == 409
            assert response.json()["detail"]["code"] == "check_in_progress"
            update = client.put(path, json={"name": "New", "address": "router.local"})
            assert update.status_code == 409
            assert update.json()["detail"]["code"] == "check_in_progress"
            assert client.get("/api/devices").json() == [device]
        finally:
            release.set()
        assert check.result(timeout=5).status_code == 200

    assert client.delete(path).status_code == 204
    assert client.get("/api/devices").json() == []
