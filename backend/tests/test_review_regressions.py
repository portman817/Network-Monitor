import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.main import create_app
from app.ping import PingResult


@pytest.mark.parametrize("operation", ["create", "check"])
def test_success_does_not_read_database_after_commit(tmp_path, operation):
    with TestClient(create_app(tmp_path / "regression.sqlite3"), raise_server_exceptions=False) as client:
        if operation == "check":
            created = client.post("/api/devices", json={"name": "Loopback", "address": "127.0.0.1"})
            device_id = created.json()["id"]
            client.app.state.ping_runner = lambda _: PingResult("online", 3.0)

        def mark_committed(session):
            session.info["committed"] = True

        def fail_post_commit_read(state):
            if state.session.info.get("committed"):
                raise OperationalError("SELECT devices", {}, Exception("read failed after commit"))

        event.listen(Session, "after_commit", mark_committed)
        event.listen(Session, "do_orm_execute", fail_post_commit_read)
        try:
            if operation == "create":
                response = client.post("/api/devices", json={"name": "Loopback", "address": "127.0.0.1"})
                assert response.status_code == 201
                assert response.json()["status"] == "unknown"
            else:
                response = client.post(f"/api/devices/{device_id}/check")
                assert response.status_code == 200
                assert response.json()["status"] == "online"
                assert response.json()["latency_ms"] == 3.0
            assert client.get("/api/devices").json() == [response.json()]
        finally:
            event.remove(Session, "do_orm_execute", fail_post_commit_read)
            event.remove(Session, "after_commit", mark_committed)


@pytest.mark.parametrize("name", ["\x00router", "rou\x00ter", "router\x00"])
def test_nul_name_returns_validation_error_without_writing(client, name):
    response = client.post("/api/devices", json={"name": name, "address": "router"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]
    assert client.get("/api/devices").json() == []


@pytest.mark.parametrize("device_id", [9223372036854775808, -9223372036854775809, 0])
def test_out_of_range_id_returns_validation_error_before_ping(client, device_id):
    client.app.state.ping_runner = lambda _: pytest.fail("Invalid ID must not invoke ping")
    response = client.post(f"/api/devices/{device_id}/check")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "device_id"]


def test_largest_sqlite_id_is_valid_but_missing(client):
    assert client.post("/api/devices/9223372036854775807/check").status_code == 404
