import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from app import ping


@pytest.mark.parametrize("target", ["localhost", "example.com", "127.0.0.2", "::1", "::ffff:127.0.0.1",
                                         "0.0.0.0", "255.255.255.255", "224.0.0.1", "127.0.0.1;whoami"])
def test_forbidden_target_never_starts_process(target, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("No DNS or subprocess may run for a forbidden target")
    monkeypatch.setattr(ping, "powershell_path", forbidden)
    import socket
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    with pytest.raises(ping.CheckError) as error:
        ping.ping_once(target)
    assert error.value.status_code == 403


def mock_run(monkeypatch, stdout, returncode=0):
    monkeypatch.setattr(ping, "powershell_path", lambda: Path("trusted/powershell.exe"))
    def run(args, **kwargs):
        assert args[0] == str(Path("trusted/powershell.exe"))
        assert kwargs["shell"] is False
        assert kwargs["timeout"] == 5
        assert json.loads(kwargs["input"]) == {
            "address": "127.0.0.1", "allowed_addresses": ["127.0.0.1"],
        }
        assert "127.0.0.1" not in args
        return SimpleNamespace(returncode=returncode, stdout=stdout)
    monkeypatch.setattr(ping.subprocess, "run", run)


@pytest.mark.parametrize("status", ["TimedOut", "DestinationHostUnreachable", "DestinationNetworkUnreachable"])
def test_offline(monkeypatch, status):
    mock_run(monkeypatch, json.dumps({"status": status, "latency_ms": 0}))
    assert ping.ping_once("127.0.0.1") == ping.PingResult("offline", None)


def test_zero_rtt_is_success(monkeypatch):
    mock_run(monkeypatch, '{"status":"Success","latency_ms":0}')
    assert ping.ping_once("127.0.0.1") == ping.PingResult("online", 0.0)


@pytest.mark.parametrize("stdout", ["broken", "[]", "null", '{}', '{"status":"Unknown"}',
    '{"status":"Success","latency_ms":-1}', '{"status":"Success","latency_ms":true}',
    '{"status":"Success","latency_ms":"1"}', '{"status":"Success","latency_ms":NaN}'])
def test_invalid_response(monkeypatch, stdout):
    mock_run(monkeypatch, stdout)
    with pytest.raises(ping.CheckError, match="ping_invalid_response"):
        ping.ping_once("127.0.0.1")


@pytest.mark.parametrize("exception, code", [(OSError(), "ping_unavailable"),
    (subprocess.TimeoutExpired("powershell", 5), "ping_process_timeout")])
def test_process_errors(monkeypatch, exception, code):
    mock_run(monkeypatch, "")
    def fail(*args, **kwargs):
        raise exception
    monkeypatch.setattr(ping.subprocess, "run", fail)
    with pytest.raises(ping.CheckError, match=code):
        ping.ping_once("127.0.0.1")


def test_failed_process(monkeypatch):
    mock_run(monkeypatch, "", returncode=1)
    with pytest.raises(ping.CheckError, match="ping_failed"):
        ping.ping_once("127.0.0.1")


def test_unsupported_platform(monkeypatch):
    monkeypatch.setattr(ping.sys, "platform", "linux")
    with pytest.raises(ping.CheckError, match="platform_unsupported"):
        ping.ping_once("127.0.0.1")


def test_limiter_concurrency_cooldown_and_cleanup():
    now = [0.0]
    limiter = ping.CheckLimiter(clock=lambda: now[0])
    with limiter.acquire(1):
        limiter.start(1)
        with pytest.raises(ping.CheckError, match="check_in_progress"):
            with limiter.acquire(1):
                pass
        with limiter.acquire(2):
            with pytest.raises(ping.CheckError, match="check_rate_limited"):
                with limiter.acquire(3):
                    pass
    assert not limiter.active
    with pytest.raises(ping.CheckError, match="check_rate_limited"):
        with limiter.acquire(1):
            limiter.start(1)
    now[0] = 5.0
    with pytest.raises(RuntimeError):
        with limiter.acquire(1):
            limiter.start(1)
            raise RuntimeError
    assert not limiter.active
    assert len(limiter.last_started) == 1
