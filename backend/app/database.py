from collections.abc import Iterator
from pathlib import Path

from fastapi import Request
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "network_monitor.sqlite3"


class Base(DeclarativeBase):
    pass


def build_engine(path: Path):
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        URL.create("sqlite", database=str(path)),
        connect_args={"check_same_thread": False, "timeout": 15},
    )


def get_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session
