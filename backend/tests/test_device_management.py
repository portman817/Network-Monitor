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
            assert client.get("/api/devices").json() == [device]
        finally:
            release.set()
        assert check.result(timeout=5).status_code == 200

    assert client.delete(path).status_code == 204
    assert client.get("/api/devices").json() == []
