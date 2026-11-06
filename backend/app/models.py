from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


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
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
