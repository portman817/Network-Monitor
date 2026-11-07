from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Event

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.models import Device
from app.ping import CheckError, PingResult


def add(client, address="127.0.0.1"):
    response = client.post("/api/devices", json={"name": "Target", "address": address})
    assert response.status_code == 201
    return response.json()["id"]


def test_printer_is_allowed(client):
    device_id = add(client, "192.168.0.247")
    assert client.get("/api/devices").json()[0]["check_allowed"] is True

    def ping(address):
        assert address == "192.168.0.247"
        return PingResult("online", 1.0)

    client.app.state.ping_runner = ping
    response = client.post(f"/api/devices/{device_id}/check")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


@pytest.mark.parametrize("result", [PingResult("online", 0.0), PingResult("offline", None)])
def test_check_persists_result_and_utc(tmp_path, result):
    path = tmp_path / "checks.sqlite3"
    with TestClient(create_app(path)) as client:
        device_id = add(client)
        client.app.state.ping_runner = lambda target: result
        response = client.post(f"/api/devices/{device_id}/check")
        assert response.status_code == 200
        saved = response.json()
        assert saved["status"] == result.status
        assert saved["latency_ms"] == result.latency_ms
        assert datetime.fromisoformat(saved["last_checked_at"]).utcoffset().total_seconds() == 0
        assert client.get("/api/devices").json() == [saved]
    with TestClient(create_app(path)) as restarted:
        assert restarted.get("/api/devices").json() == [saved]


@pytest.mark.parametrize("address", ["localhost", "example.com", "127.0.0.2", "::1", "192.168.1.1"])
def test_api_denies_before_runner(client, address):
    device_id = add(client, address)
    client.app.state.ping_runner = lambda _: pytest.fail("Forbidden runner call")
    before = client.get("/api/devices").json()
    assert client.post(f"/api/devices/{device_id}/check").status_code == 403
    assert client.get("/api/devices").json() == before


@pytest.mark.parametrize("status, code", [(503, "ping_failed"), (504, "ping_process_timeout")])
def test_technical_error_preserves_measurement(client, status, code):
    device_id = add(client)
    with Session(client.app.state.engine) as session:
        device = session.get(Device, device_id)
        device.status = "online"
        device.latency_ms = 2
        device.last_checked_at = datetime(2026, 11, 6, tzinfo=timezone.utc)
        session.commit()
    before = client.get("/api/devices").json()
    def fail(_):
        raise CheckError(status, code)
    client.app.state.ping_runner = fail
    response = client.post(f"/api/devices/{device_id}/check")
    assert response.status_code == status
    assert response.json()["detail"]["code"] == code
    assert client.get("/api/devices").json() == before
    assert not client.app.state.check_limiter.active


def test_missing_and_cooldown(client):
    assert client.post("/api/devices/999/check").status_code == 404
    device_id = add(client)
    client.app.state.ping_runner = lambda _: PingResult("online", 1.0)
    assert client.post(f"/api/devices/{device_id}/check").status_code == 200
    response = client.post(f"/api/devices/{device_id}/check")
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "5"


def test_storage_error_does_not_overwrite_previous_data(client, monkeypatch):
    from sqlalchemy.exc import OperationalError

    device_id = add(client)
    before = client.get("/api/devices").json()
    client.app.state.ping_runner = lambda _: PingResult("online", 1)
    def fail_commit(self):
        raise OperationalError("UPDATE devices", {}, Exception("database locked"))
    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.post(f"/api/devices/{device_id}/check")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "storage_unavailable"
    assert client.get("/api/devices").json() == before
    assert not client.app.state.check_limiter.active


def test_parallel_same_device_and_health(client):
    device_id = add(client)
    entered, release = Event(), Event()
    def wait(_):
        entered.set()
        assert release.wait(3)
        return PingResult("online", 1)
    client.app.state.ping_runner = wait
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(client.post, f"/api/devices/{device_id}/check")
        try:
            assert entered.wait(3)
            assert client.post(f"/api/devices/{device_id}/check").status_code == 409
            assert client.get("/api/health").json() == {"status": "ok"}
            assert client.get("/api/devices").status_code == 200
        finally:
            release.set()
        assert future.result().status_code == 200
