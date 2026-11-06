import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, build_engine
from app.models import Device


def test_defaults_persistence_and_database_uniqueness(tmp_path):
    path = tmp_path / "devices.sqlite3"
    engine = build_engine(path)
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            device = Device(name="Router", address="192.0.2.1")
            session.add(device)
            session.commit()
            assert device.id == 1
            assert device.status == "unknown"
            assert device.latency_ms is None
            assert device.last_checked_at is None
    finally:
        engine.dispose()
    engine = build_engine(path)
    try:
        with Session(engine) as session:
            assert session.get(Device, 1).name == "Router"
            session.add(Device(name="Duplicate", address="192.0.2.1"))
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()
            assert session.get(Device, 1).address == "192.0.2.1"
    finally:
        engine.dispose()
