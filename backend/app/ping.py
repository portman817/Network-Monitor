import base64
import ctypes
import ipaddress
import json
import math
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

ALLOWED_ADDRESSES = frozenset({"127.0.0.1", "192.168.0.247"})
ICMP_TIMEOUT_MS = 1000
PROCESS_TIMEOUT_SECONDS = 5
CHECK_INTERVAL_SECONDS = 5
MAX_CONCURRENT_CHECKS = 2


class CheckError(Exception):
    def __init__(self, status_code: int, code: str):
        self.status_code = status_code
        self.code = code
        super().__init__(code)


def allowed_target(address: str) -> str:
    # Domains are deliberately rejected without DNS resolution.
    try:
        target = str(ipaddress.ip_address(address))
    except ValueError:
        raise CheckError(403, "target_forbidden") from None
    if target not in ALLOWED_ADDRESSES:
        raise CheckError(403, "target_forbidden")
    return target


@dataclass(frozen=True)
class PingResult:
    status: str
    latency_ms: float | None


SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
try {
    $data = [Console]::In.ReadToEnd() | ConvertFrom-Json
    $ip = [System.Net.IPAddress]::Parse($data.address)
    if ($ip.ToString() -notin $data.allowed_addresses) { throw 'Forbidden target' }
    $ping = New-Object System.Net.NetworkInformation.Ping
    try {
        $reply = $ping.Send($ip, 1000)
        @{status=$reply.Status.ToString(); latency_ms=$reply.RoundtripTime} | ConvertTo-Json -Compress
    } finally { $ping.Dispose() }
} catch { exit 1 }
"""


def powershell_path() -> Path:
    if sys.platform != "win32":
        raise CheckError(503, "platform_unsupported")
    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
    if not length or length >= len(buffer):
        raise CheckError(503, "ping_unavailable")
    return Path(buffer.value) / "WindowsPowerShell" / "v1.0" / "powershell.exe"


def ping_once(address: str) -> PingResult:
    target = allowed_target(address)
    executable = powershell_path()
    encoded = base64.b64encode(SCRIPT.encode("utf-16-le")).decode("ascii")
    try:
        completed = subprocess.run(
            [str(executable), "-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
            input=json.dumps({"address": target, "allowed_addresses": sorted(ALLOWED_ADDRESSES)}),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=PROCESS_TIMEOUT_SECONDS,
            shell=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        # subprocess.run kills and waits for the child before raising.
        raise CheckError(504, "ping_process_timeout") from None
    except (OSError, UnicodeError):
        raise CheckError(503, "ping_unavailable") from None
    if completed.returncode != 0:
        raise CheckError(503, "ping_failed")
    try:
        data = json.loads(completed.stdout)
        status = data["status"]
        if status == "Success":
            latency = data["latency_ms"]
            if isinstance(latency, bool) or not isinstance(latency, (int, float)):
                raise ValueError
            if not math.isfinite(latency) or latency < 0:
                raise ValueError
            return PingResult("online", float(latency))
        if status in {"TimedOut", "DestinationHostUnreachable", "DestinationNetworkUnreachable",
                      "DestinationUnreachable", "DestinationPortUnreachable", "DestinationProtocolUnreachable"}:
            return PingResult("offline", None)
    except (ValueError, KeyError, TypeError):
        pass
    raise CheckError(503, "ping_invalid_response")


class CheckLimiter:
    """Limits apply to a single backend process; no waiting queue."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.lock = threading.Lock()
        self.active: set[int] = set()
        self.last_started: dict[int, float] = {}

    @contextmanager
    def acquire(self, device_id: int):
        with self.lock:
            now = self.clock()
            self.last_started = {key: value for key, value in self.last_started.items()
                                 if now - value < CHECK_INTERVAL_SECONDS}
            if device_id in self.active:
                raise CheckError(409, "check_in_progress")
            if device_id in self.last_started or len(self.active) >= MAX_CONCURRENT_CHECKS:
                raise CheckError(429, "check_rate_limited")
            self.active.add(device_id)
            self.last_started[device_id] = now
        try:
            yield
        finally:
            with self.lock:
                self.active.remove(device_id)
