from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from .database import Base


class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("UTC timestamp must be timezone-aware")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=timezone.utc) if value is not None else None


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint("length(name) BETWEEN 1 AND 100", name="valid_device_name"),
        CheckConstraint("latency_ms IS NULL OR latency_ms >= 0", name="nonnegative_latency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(253), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="unknown", server_default=text("'unknown'"))
    latency_ms: Mapped[float | None] = mapped_column(Float, default=None)
    last_checked_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), default=None)
