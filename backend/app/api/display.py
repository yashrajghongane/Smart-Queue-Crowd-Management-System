from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Token, TokenStatus, Department, Room

router = APIRouter()

@router.get("/{department_id}")
def get_display(department_id: str, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    current_token = db.query(Token).filter(
        Token.department_id == department_id,
        Token.status == TokenStatus.SERVING.value
    ).order_by(Token.called_at.desc()).first()

    next_token = db.query(Token).filter(
        Token.department_id == department_id,
        Token.status == TokenStatus.WAITING.value
    ).order_by(Token.created_at.asc()).first()

    room_name = None
    if current_token and current_token.room_id:
        room = db.query(Room).filter(Room.id == current_token.room_id).first()
        if room:
            room_name = room.name_or_number

    return {
        "department": dept.name,
        "current_token": current_token.display_token if current_token else None,
        "next_token": next_token.display_token if next_token else None,
        "room": room_name
    }
