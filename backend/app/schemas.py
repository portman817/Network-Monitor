import ipaddress
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from .ping import ALLOWED_ADDRESSES

LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", re.ASCII)


def normalize_address(value: str) -> str:
    value = value.strip()
    if not value or "%" in value:
        raise ValueError("Invalid IP address or domain name")
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        pass
    value = value.removesuffix(".")
    try:
        domain = value.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Invalid domain name") from exc
    labels = domain.split(".")
    if (
        len(domain) > 253
        or not all(LABEL.fullmatch(label) for label in labels)
        or all(label.isdigit() for label in labels)
    ):
        raise ValueError("Invalid IP address or domain name")
    for label in labels:
        if label.startswith("xn--"):
            try:
                label.encode("ascii").decode("idna")
            except UnicodeError as exc:
                raise ValueError("Invalid international domain name") from exc
    return domain


class DeviceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=1024)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("Device name must not contain a null character")
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        return normalize_address(value)


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    status: str
    latency_ms: float | None
    last_checked_at: datetime | None

    @computed_field
    @property
    def check_allowed(self) -> bool:
        return self.address in ALLOWED_ADDRESSES
