from typing import Annotated

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Device
from ..schemas import DeviceCreate, DeviceRead
from ..ping import CheckError, allowed_target

router = APIRouter(prefix="/api/devices", tags=["devices"])
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[DeviceRead])
def list_devices(session: DatabaseSession):
    return session.scalars(select(Device).order_by(Device.id)).all()


@router.post("", response_model=DeviceRead, status_code=201)
def create_device(payload: DeviceCreate, session: DatabaseSession):
    device = Device(**payload.model_dump())
    session.add(device)
    try:
        session.flush()
        response = DeviceRead.model_validate(device)
        session.commit()
    except IntegrityError:
        session.rollback()
        if session.scalar(select(Device.id).where(Device.address == payload.address)) is not None:
            raise HTTPException(status_code=409, detail={"code": "duplicate_address"}) from None
        raise
    return response


@router.post("/{device_id}/check", response_model=DeviceRead)
def check_device(request: Request, device_id: Annotated[int, Path(ge=1, le=9223372036854775807)]):
    engine = request.app.state.engine
    try:
        # Close the read transaction before waiting for a network response.
        with Session(engine) as session:
            device = session.get(Device, device_id)
            if device is None:
                raise HTTPException(404, detail={"code": "device_not_found"})
            target = allowed_target(device.address)
        with request.app.state.check_limiter.acquire(device_id):
            result = request.app.state.ping_runner(target)
            checked_at = datetime.now(timezone.utc)
            with Session(engine) as session:
                device = session.get(Device, device_id)
                if device is None:
                    raise HTTPException(404, detail={"code": "device_not_found"})
                if device.address != target:
                    raise HTTPException(409, detail={"code": "device_changed"})
                device.status = result.status
                device.latency_ms = result.latency_ms
                device.last_checked_at = checked_at
                session.flush()
                response = DeviceRead.model_validate(device)
                session.commit()
                return response
    except CheckError as exc:
        headers = {"Retry-After": "5"} if exc.status_code == 429 else None
        raise HTTPException(exc.status_code, detail={"code": exc.code}, headers=headers) from None
    except SQLAlchemyError:
        raise HTTPException(503, detail={"code": "storage_unavailable"}) from None
