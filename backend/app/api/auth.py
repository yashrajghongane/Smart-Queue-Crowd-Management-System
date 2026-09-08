from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

from app.database import get_db
from app.auth_models import Staff, StaffSession, pwd_context

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.username == req.username).first()
    if not staff or not pwd_context.verify(req.password, staff.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    import hashlib
    # Create session
    session_id = str(uuid.uuid4())
    session_hash = hashlib.sha256(session_id.encode()).hexdigest()

    staff_session = StaffSession(
        staff_id=staff.id,
        session_identifier_hash=session_hash,
        expires_at=datetime.utcnow() + timedelta(hours=12)
    )
    db.add(staff_session)
    staff.last_login_at = datetime.utcnow()
    db.commit()

    # Normally use secure/httponly cookies. Here returning token or simple cookie for demo
    response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")

    return {
        "staff": {
            "id": staff.id,
            "display_name": staff.display_name,
            "role": staff.role
        }
    }

def get_current_staff(request: Request, db: Session = Depends(get_db)) -> Staff:
    # Very naive check for demo purposes. Real app uses proper session parsing from cookie
    session_id = request.cookies.get("session_id")
    if not session_id:
        # Check header just in case for test client
        session_id = request.headers.get("x-session-id")
        if not session_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

    import hashlib
    session_hash = hashlib.sha256(session_id.encode()).hexdigest()
    valid_session = db.query(StaffSession).filter(
        StaffSession.session_identifier_hash == session_hash,
        StaffSession.expires_at > datetime.utcnow(),
        StaffSession.revoked_at == None
    ).first()

    if not valid_session:
        raise HTTPException(status_code=401, detail="Unauthorized")

    staff = db.query(Staff).filter(Staff.id == valid_session.staff_id).first()
    return staff

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_id")
    return {"status": "ok"}

@router.get("/me")
def me(staff: Staff = Depends(get_current_staff)):
    return {
        "staff": {
            "id": staff.id,
            "display_name": staff.display_name,
            "role": staff.role
        }
    }
