from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Token, TokenStatus, Department, Room

router = APIRouter()

@router.get("/{status_access_id}")
def get_status(status_access_id: str, db: Session = Depends(get_db)):
    token = db.query(Token).filter(Token.status_access_id == status_access_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Status not found")

    department = db.query(Department).filter(Department.id == token.department_id).first()
    room = db.query(Room).filter(Room.id == token.room_id).first() if token.room_id else None

    current_token = db.query(Token).filter(
        Token.department_id == token.department_id,
        Token.status == TokenStatus.SERVING.value
    ).order_by(Token.called_at.desc()).first()

    # Very naive "patients ahead" calculation.
    # In a real system, you'd count waiting tokens created before this one.
    patients_ahead = db.query(Token).filter(
        Token.department_id == token.department_id,
        Token.status == TokenStatus.WAITING.value,
        Token.created_at < token.created_at
    ).count()

    estimated_wait = patients_ahead * 5 # Naive 5 mins per patient

    return {
        "display_token": token.display_token,
        "current_token": current_token.display_token if current_token else None,
        "patients_ahead": patients_ahead,
        "estimated_wait_minutes": estimated_wait,
        "department": department.name if department else "Unknown",
        "room": room.name_or_number if room else None,
        "status": token.status
    }
