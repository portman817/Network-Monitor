import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


@pytest.mark.parametrize("method", ["get", "post"])
def test_device_routes_report_storage_failure(client, monkeypatch, method):
    def fail(*args, **kwargs):
        raise OperationalError("test", {}, Exception("private database diagnostic"))
    if method == "get":
        monkeypatch.setattr(Session, "scalars", fail)
        response = client.get("/api/devices")
    else:
        monkeypatch.setattr(Session, "commit", fail)
        response = client.post("/api/devices", json={"name": "Local", "address": "127.0.0.1"})
    assert response.status_code == 503
    assert response.json() == {"detail": {"code": "storage_unavailable"}}


def test_duplicate_has_machine_readable_code(client):
    payload = {"name": "Local", "address": "127.0.0.1"}
    assert client.post("/api/devices", json=payload).status_code == 201
    response = client.post("/api/devices", json=payload)
    assert response.status_code == 409
    assert response.json() == {"detail": {"code": "duplicate_address"}}
