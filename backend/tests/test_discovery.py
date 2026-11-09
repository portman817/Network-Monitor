from ipaddress import IPv4Network

from app import ping
from app.ping import CheckError, PingResult


def test_discovery_lists_and_scans_only_small_configured_subnets(client, monkeypatch):
    subnet = "192.168.50.0/29"
    monkeypatch.setattr(ping, "ALLOWED_NETWORKS", (IPv4Network(subnet), IPv4Network("10.0.0.0/16")))
    addresses = []

    def run_ping(address):
        addresses.append(address)
        if address.endswith(".2"):
            return PingResult("online", 1.5)
        return PingResult("offline", None)

    client.app.state.ping_runner = run_ping
    path = "/api/devices/discovery"
    assert client.get(path).json() == [subnet]
    for denied in ("10.0.0.0/16", "192.168.50.0/30", "192.168.51.0/24", "127.0.0.1/32"):
        assert client.post(path, json={"subnet": denied, "offset": 0}).status_code == 403
    assert addresses == []

    first = client.post(path, json={"subnet": subnet, "offset": 0})
    assert first.json() == {
        "found": [{"address": "192.168.50.2", "latency_ms": 1.5}],
        "checked": 4, "total": 6, "next_offset": 4, "skipped": 0,
    }
    assert len(addresses) == 4
    second = client.post(path, json={"subnet": subnet, "offset": 4})
    assert second.json() == {"found": [], "checked": 6, "total": 6, "next_offset": None, "skipped": 0}
    assert addresses == [f"192.168.50.{host}" for host in range(1, 7)]
    assert client.get("/api/devices").json() == []


def test_discovery_skips_one_ping_timeout_and_keeps_results(client, monkeypatch):
    subnet = "192.168.50.0/29"
    monkeypatch.setattr(ping, "ALLOWED_NETWORKS", (IPv4Network(subnet),))

    def run_ping(address):
        if address.endswith(".2"):
            raise CheckError(504, "ping_process_timeout")
        return PingResult("online", 1.5)

    client.app.state.ping_runner = run_ping
    response = client.post("/api/devices/discovery", json={"subnet": subnet, "offset": 0})
    assert response.status_code == 200
    batch = response.json()
    assert batch["skipped"] == 1
    assert batch["next_offset"] == 4
    assert [host["address"] for host in batch["found"]] == [
        "192.168.50.1", "192.168.50.3", "192.168.50.4",
    ]

    def unavailable(address):
        raise CheckError(503, "ping_unavailable")

    client.app.state.ping_runner = unavailable
    response = client.post("/api/devices/discovery", json={"subnet": subnet, "offset": 4})
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "ping_unavailable"
