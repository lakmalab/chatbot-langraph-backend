from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DBSession
from app.db.connection import get_db
from app.schemas.session import SessionCreate, SessionResponse
from app.service.session_service import SessionService

router = APIRouter(prefix="/api/v2/session", tags=["Session"])

@router.post("/create", response_model=SessionResponse)
async def create_session(
        request: Request,
        db: DBSession = Depends(get_db)
):
    session_service = SessionService(db)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    session_data = SessionCreate(
        ip_address=ip_address,
        user_agent=user_agent
    )

    new_session = session_service.create_session(session_data)

    return new_session