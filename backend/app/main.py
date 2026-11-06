from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .database import Base, DEFAULT_DATABASE_PATH, build_engine
from .routers.devices import router
from .ping import CheckLimiter, ping_once


async def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app(database_path: Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        engine = build_engine(database_path if database_path is not None else DEFAULT_DATABASE_PATH)
        try:
            Base.metadata.create_all(engine)
            application.state.engine = engine
            application.state.check_limiter = CheckLimiter()
            application.state.ping_runner = ping_once
            yield
        finally:
            engine.dispose()

    application = FastAPI(title="Network Monitor", lifespan=lifespan)

    @application.exception_handler(SQLAlchemyError)
    async def storage_error(request, exc):
        return JSONResponse(status_code=503, content={"detail": {"code": "storage_unavailable"}})

    application.add_api_route("/api/health", health, methods=["GET"])
    application.include_router(router)
    return application


app = create_app()
