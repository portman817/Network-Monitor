from typing import Annotated

from datetime import datetime, timezone
from ipaddress import IPv4Network

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from .. import ping
from ..database import get_session
from ..models import Device
from ..schemas import DeviceCreate, DeviceRead
from ..ping import CheckError, allowed_target

router = APIRouter(prefix="/api/devices", tags=["devices"])
DatabaseSession = Annotated[Session, Depends(get_session)]


class DiscoveryBatch(BaseModel):
    subnet: str
    offset: int = Field(ge=0, le=254)


@router.get("/discovery")
def discovery_subnets() -> list[str]:
    return sorted({str(network) for network in ping.ALLOWED_NETWORKS if network.prefixlen >= 24})


@router.post("/discovery")
def discover_devices(payload: DiscoveryBatch, request: Request):
    if payload.subnet not in discovery_subnets():
        raise HTTPException(403, detail={"code": "target_forbidden"})

    network = IPv4Network(payload.subnet)
    hosts = list(network.hosts())
    batch = hosts[payload.offset:payload.offset + 4]
    found = []
    skipped = 0
    try:
        # Device IDs are positive. Reserve one of the existing Ping slots.
        with request.app.state.check_limiter.acquire(0):
            for host in batch:
                address = allowed_target(str(host))
                try:
                    result = request.app.state.ping_runner(address)
                except CheckError as exc:
                    if exc.code != "ping_process_timeout":
                        raise
                    skipped += 1
                    continue
                if result.status == "online":
                    found.append({"address": address, "latency_ms": result.latency_ms})
    except CheckError as exc:
        raise HTTPException(exc.status_code, detail={"code": exc.code}) from None

    end = min(payload.offset + len(batch), len(hosts))
    return {"found": found, "checked": end, "total": len(hosts), "skipped": skipped,
            "next_offset": end if end < len(hosts) else None}


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


@router.put("/{device_id}", response_model=DeviceRead)
def update_device(payload: DeviceCreate, request: Request,
                  device_id: Annotated[int, Path(ge=1, le=9223372036854775807)],
                  session: DatabaseSession):
    limiter = request.app.state.check_limiter
    with limiter.lock:
        if device_id in limiter.active:
            raise HTTPException(409, detail={"code": "check_in_progress"})
        device = session.get(Device, device_id)
        if device is None:
            raise HTTPException(404, detail={"code": "device_not_found"})
        address_changed = device.address != payload.address
        device.name = payload.name
        if address_changed:
            device.address = payload.address
            device.status = "unknown"
            device.latency_ms = None
            device.last_checked_at = None
        try:
            session.flush()
            response = DeviceRead.model_validate(device)
            session.commit()
        except IntegrityError:
            session.rollback()
            if session.scalar(select(Device.id).where(Device.address == payload.address,
                                                       Device.id != device_id)) is not None:
                raise HTTPException(409, detail={"code": "duplicate_address"}) from None
            raise
        if address_changed:
            limiter.last_started.pop(device_id, None)
        return response


@router.delete("/{device_id}", status_code=204)
def delete_device(request: Request, device_id: Annotated[int, Path(ge=1, le=9223372036854775807)],
                  session: DatabaseSession):
    limiter = request.app.state.check_limiter
    with limiter.lock:
        if device_id in limiter.active:
            raise HTTPException(409, detail={"code": "check_in_progress"})
        result = session.execute(delete(Device).where(Device.id == device_id))
        if not result.rowcount:
            raise HTTPException(404, detail={"code": "device_not_found"})
        session.commit()
        limiter.last_started.pop(device_id, None)


@router.post("/{device_id}/check", response_model=DeviceRead)
def check_device(request: Request, device_id: Annotated[int, Path(ge=1, le=9223372036854775807)]):
    engine = request.app.state.engine
    limiter = request.app.state.check_limiter
    try:
        with limiter.acquire(device_id):
            # Close the read transaction before waiting for a network response.
            with Session(engine) as session:
                device = session.get(Device, device_id)
                if device is None:
                    raise HTTPException(404, detail={"code": "device_not_found"})
                target = allowed_target(device.address)
            limiter.start(device_id)
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
