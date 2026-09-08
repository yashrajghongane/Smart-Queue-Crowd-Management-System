from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, asc
from fastapi import HTTPException
from datetime import datetime
import json

from app.models import Token, TokenStatus, PriorityType, Visit, Department, Room
from app.auth_models import QueueEvent

def _record_event(db: Session, token: Token, action: str, from_status: str, to_status: str, actor_id: str, actor_type: str = "STAFF"):
    evt = QueueEvent(
        token_id=token.id,
        visit_id=token.visit_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        from_status=from_status,
        to_status=to_status,
    )
    db.add(evt)

def call_next(db: Session, department_id: str, actor_id: str, room_id: str = None) -> Token:
    # Find next eligible token (WAITING or HOLD)
    # Order by EMERGENCY -> PRIORITY -> NORMAL, then by created_at (FIFO)

    # Python map enum to priority sort order
    priority_order = {
        PriorityType.EMERGENCY.value: 1,
        PriorityType.PRIORITY.value: 2,
        PriorityType.NORMAL.value: 3
    }

    eligible = db.query(Token).filter(
        Token.department_id == department_id,
        Token.status.in_([TokenStatus.WAITING.value, TokenStatus.HOLD.value])
    ).all()

    if not eligible:
        raise HTTPException(status_code=400, detail={"error": "QUEUE_EMPTY", "message": "No tokens waiting."})

    # Sort in-memory for simpler logic, or construct complex SQL case statement.
    # For small queues, in-memory is fine.
    eligible.sort(key=lambda t: (priority_order.get(t.priority, 3), t.created_at))
    next_token = eligible[0]

    from_status = next_token.status
    next_token.status = TokenStatus.SERVING.value
    next_token.called_at = datetime.utcnow()
    if room_id:
        next_token.room_id = room_id

    _record_event(db, next_token, "CALL_NEXT", from_status, next_token.status, actor_id)

    db.commit()
    db.refresh(next_token)
    return next_token

def transition_token(db: Session, token_id: str, action: str, target_status: str, actor_id: str) -> Token:
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Token not found"})

    from_status = token.status
    if from_status == TokenStatus.COMPLETED.value or from_status == TokenStatus.SKIPPED.value:
        raise HTTPException(status_code=400, detail={"error": "INVALID_STATE_TRANSITION", "message": "Token is already in terminal state"})

    token.status = target_status
    if target_status == TokenStatus.COMPLETED.value:
        token.completed_at = datetime.utcnow()

    _record_event(db, token, action, from_status, target_status, actor_id)
    db.commit()
    db.refresh(token)
    return token

def transfer_token(db: Session, token_id: str, target_department_id: str, actor_id: str) -> dict:
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    target_dept = db.query(Department).filter(Department.id == target_department_id).first()
    if not target_dept:
        raise HTTPException(status_code=400, detail="Invalid target department")

    # Mark old as transferred/completed
    from_status = token.status
    token.status = TokenStatus.COMPLETED.value
    _record_event(db, token, "TRANSFER", from_status, token.status, actor_id, metadata_json=json.dumps({"target_dept": target_dept.name}))

    # Create new visit/token
    new_visit = Visit(patient_id=token.visit.patient_id, department_id=target_department_id)
    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)

    count = db.query(Token).filter(Token.department_id == target_department_id).count()
    new_display_token = f"{target_dept.code}{count + 101}"

    room = db.query(Room).filter(Room.department_id == target_department_id, Room.active == True).first()

    import uuid
    new_token = Token(
        visit_id=new_visit.id,
        department_id=target_department_id,
        display_token=new_display_token,
        status=TokenStatus.WAITING.value,
        room_id=room.id if room else None,
        status_access_id=str(uuid.uuid4())
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    _record_event(db, new_token, "TRANSFERRED_IN", "NONE", new_token.status, actor_id, metadata_json=json.dumps({"source_token": token.display_token}))
    db.commit()

    return {
        "source_token": token.display_token,
        "target_token": new_token.display_token,
        "target_department": target_dept.name,
        "status": new_token.status
    }
