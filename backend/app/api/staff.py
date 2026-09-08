from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.api.auth import get_current_staff, RequireRole
from app.auth_models import Staff
from app.core import queue
from app.models import Department, Token, TokenStatus, PriorityType

router = APIRouter()

@router.get("/queues")
def get_queues(db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    departments = db.query(Department).filter(Department.active == True).all()
    res = []
    for d in departments:
        waiting_count = db.query(Token).filter(Token.department_id == d.id, Token.status == TokenStatus.WAITING.value).count()
        current_token = db.query(Token).filter(Token.department_id == d.id, Token.status == TokenStatus.SERVING.value).order_by(Token.called_at.desc()).first()

        res.append({
            "department_id": d.id,
            "name": d.name,
            "waiting_count": waiting_count,
            "current_token": current_token.display_token if current_token else None,
            "current_token_id": current_token.id if current_token else None,
            "room": "2" # Stubbed for now
        })
    return {"departments": res}

@router.post("/queue/{department_id}/next")
def call_next(department_id: str, db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    token = queue.call_next(db, department_id, staff.id)
    return {
        "token_id": token.id,
        "display_token": token.display_token,
        "status": token.status,
        "room": "2" # Stubbed
    }

@router.post("/token/{token_id}/hold")
def hold_token(token_id: str, db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    token = queue.transition_token(db, token_id, "HOLD", TokenStatus.HOLD.value, staff.id)
    return {"token_id": token.id, "display_token": token.display_token, "status": token.status}

@router.post("/token/{token_id}/recall")
def recall_token(token_id: str, db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    # Same as WAITING but records RECALL
    token = queue.transition_token(db, token_id, "RECALL", TokenStatus.WAITING.value, staff.id)
    return {"token_id": token.id, "display_token": token.display_token, "status": token.status}

@router.post("/token/{token_id}/skip")
def skip_token(token_id: str, db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    token = queue.transition_token(db, token_id, "SKIP", TokenStatus.SKIPPED.value, staff.id)
    return {"token_id": token.id, "display_token": token.display_token, "status": token.status}

@router.post("/token/{token_id}/complete")
def complete_token(token_id: str, db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    token = queue.transition_token(db, token_id, "COMPLETE", TokenStatus.COMPLETED.value, staff.id)
    return {"token_id": token.id, "display_token": token.display_token, "status": token.status}

class TransferRequest(BaseModel):
    target_department_id: str

@router.post("/token/{token_id}/transfer")
def transfer_token(token_id: str, req: TransferRequest, db: Session = Depends(get_db), staff: Staff = Depends(get_current_staff)):
    return queue.transfer_token(db, token_id, req.target_department_id, staff.id)

class PriorityRequest(BaseModel):
    priority: str

@router.post("/token/{token_id}/priority")
def priority_token(token_id: str, req: PriorityRequest, db: Session = Depends(get_db), staff: Staff = Depends(RequireRole(["ADMIN"]))):
    if req.priority not in [PriorityType.NORMAL.value, PriorityType.PRIORITY.value, PriorityType.EMERGENCY.value]:
        raise HTTPException(status_code=400, detail="Invalid priority")

    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    token.priority = req.priority
    db.commit()
    return {"token_id": token.id, "display_token": token.display_token, "priority": token.priority}
