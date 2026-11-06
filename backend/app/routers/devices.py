from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Device
from ..schemas import DeviceCreate, DeviceRead

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
        session.commit()
    except IntegrityError:
        session.rollback()
        if session.scalar(select(Device.id).where(Device.address == payload.address)) is not None:
            raise HTTPException(status_code=409, detail="Device address already exists") from None
        raise
    session.refresh(device)
    return device
