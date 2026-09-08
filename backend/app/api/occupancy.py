from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.occupancy_models import Zone, Device, OccupancyEvent, OccupancyState
from app.auth_models import pwd_context

router = APIRouter()

class OccupancyEventRequest(BaseModel):
    event_type: str # ENTRY or EXIT
    event_id: str
    occurred_at: str

# Naive device auth for demo. Prod would use a proper API key header mechanism
def authenticate_device(request: Request, device_id: str, db: Session = Depends(get_db)):
    # Suppose X-Device-Secret is used
    secret = request.headers.get("X-Device-Secret")
    if not secret:
        raise HTTPException(status_code=401, detail="Unauthorized device")

    device = db.query(Device).filter(Device.id == device_id, Device.active == True).first()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device")

    if not pwd_context.verify(secret, device.device_secret_hash_or_equivalent):
        raise HTTPException(status_code=401, detail="Unauthorized device")

    return device

@router.post("/devices/{device_id}/events")
def create_event(
    device_id: str,
    req: OccupancyEventRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    device = authenticate_device(request, device_id, db)

    if req.event_type not in ["ENTRY", "EXIT"]:
        raise HTTPException(status_code=400, detail="Invalid event_type")

    # Idempotency check
    existing = db.query(OccupancyEvent).filter(OccupancyEvent.event_id == req.event_id).first()
    if existing:
        return {"status": "ok", "message": "Event already processed"}

    # Process event
    evt = OccupancyEvent(
        device_id=device.id,
        zone_id=device.zone_id,
        event_id=req.event_id,
        event_type=req.event_type,
        occurred_at=datetime.fromisoformat(req.occurred_at.replace("Z", "+00:00"))
    )
    db.add(evt)

    # Update State
    state = db.query(OccupancyState).filter(OccupancyState.zone_id == device.zone_id).first()
    if not state:
        zone = db.query(Zone).filter(Zone.id == device.zone_id).first()
        state = OccupancyState(zone_id=device.zone_id, current_count=0, capacity=zone.capacity)
        db.add(state)

    if req.event_type == "ENTRY":
        state.current_count += 1
    elif req.event_type == "EXIT":
        state.current_count = max(0, state.current_count - 1)

    device.last_seen_at = datetime.utcnow()
    db.commit()

    return {"status": "ok"}

@router.get("/zones/{zone_id}/occupancy")
def get_occupancy(zone_id: str, db: Session = Depends(get_db)):
    state = db.query(OccupancyState).filter(OccupancyState.zone_id == zone_id).first()
    if not state:
        zone = db.query(Zone).filter(Zone.id == zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail="Zone not found")
        state = OccupancyState(zone_id=zone_id, current_count=0, capacity=zone.capacity)

    # Calculate level
    ratio = state.current_count / max(1, state.capacity)
    level = "NORMAL"
    if ratio >= 0.9:
        level = "CRITICAL"
    elif ratio >= 0.7:
        level = "HIGH"
    elif ratio >= 0.5:
        level = "MODERATE"

    return {
        "zone_id": zone_id,
        "current_count": state.current_count,
        "capacity": state.capacity,
        "level": level,
        "estimated": True,
        "updated_at": state.updated_at.isoformat() + "Z" if state.updated_at else datetime.utcnow().isoformat() + "Z"
    }
