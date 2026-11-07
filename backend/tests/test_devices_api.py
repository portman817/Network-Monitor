from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_empty_and_health(client):
    assert client.get("/api/devices").json() == []
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("address, expected", [
    ("192.0.2.1", "192.0.2.1"),
    ("2001:0db8::1", "2001:db8::1"),
    (" EXAMPLE.COM. ", "example.com"),
    ("router", "router"),
    ("bücher.example", "xn--bcher-kva.example"),
])
def test_create_and_list(client, address, expected):
    response = client.post("/api/devices", json={"name": " Router ", "address": address})
    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "name": "Router", "address": expected, "status": "unknown",
        "latency_ms": None, "last_checked_at": None, "check_allowed": False,
    }
    response_list = client.get("/api/devices")
    assert response_list.status_code == 200
    assert response_list.json() == [response.json()]


@pytest.mark.parametrize("address", [
    "", " ", "999.1.1.1", "192.168.001.1", "https://example.com", "example.com:80",
    "host/path", "bad_name", "-bad.example", "bad-.example", "a..b", "::zz",
    "fe80::1%eth0", "a" * 64 + ".example", ".", "123", "xn--.example",
    ".".join(["a" * 63] * 4),
])
def test_invalid_addresses(client, address):
    assert client.post("/api/devices", json={"name": "Router", "address": address}).status_code == 422
    assert client.get("/api/devices").json() == []


@pytest.mark.parametrize("payload", [
    {}, {"name": "x"}, {"name": "", "address": "router"},
    {"name": "   ", "address": "router"}, {"name": "x" * 101, "address": "router"},
    {"name": "x", "address": "router", "status": "up"},
    {"name": "x", "address": None}, {"name": 123, "address": "router"},
])
def test_invalid_payload(client, payload):
    assert client.post("/api/devices", json=payload).status_code == 422


@pytest.mark.parametrize("first, duplicate", [
    ("Example.COM", "example.com."),
    ("2001:db8::1", "2001:0db8:0:0:0:0:0:1"),
    ("192.0.2.1", "192.0.2.1"),
    ("bücher.example", "xn--bcher-kva.example"),
])
def test_duplicates_and_recovery(client, first, duplicate):
    assert client.post("/api/devices", json={"name": "A", "address": first}).status_code == 201
    assert client.post("/api/devices", json={"name": "B", "address": duplicate}).status_code == 409
    assert client.post("/api/devices", json={"name": "C", "address": "other.example"}).status_code == 201
    assert [item["id"] for item in client.get("/api/devices").json()] == [1, 2]


def test_concurrent_duplicate(client):
    def create(_):
        return client.post("/api/devices", json={"name": "Router", "address": "router"}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(create, range(2))) == [201, 409]
    assert len(client.get("/api/devices").json()) == 1


def test_restart_persistence(tmp_path):
    path = tmp_path / "persistent.sqlite3"
    with TestClient(create_app(path)) as first:
        response = first.post("/api/devices", json={"name": "Router", "address": "192.0.2.1"})
        assert response.status_code == 201
        saved = response.json()
    with TestClient(create_app(path)) as second:
        assert second.get("/api/devices").json() == [saved]


def test_validation_does_not_resolve_dns(client, monkeypatch):
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("Network access during validation")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket, "gethostbyname", forbidden)
    assert client.post("/api/devices", json={"name": "A", "address": "example.invalid"}).status_code == 201
