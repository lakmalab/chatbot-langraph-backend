import uuid
from datetime import datetime, timedelta

from core.config import settings
from schemas.session import SessionCreate
from models.session import Session
class SessionService:
    def __init__(self,DBSession):
        self.db = DBSession

    def create_session(self,session_data: SessionCreate) -> Session:
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        new_session = Session(
            session_id=session_id,
            ip_address=session_data.ip_address,
            user_agent=session_data.user_agent,
            expires_at=expires_at
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def is_session_valid(self, session_id: str) -> bool:
        session = self.db.query(Session).filter(Session.session_id == session_id).first()

        if not session:
            return False

        if session.expires_at and session.expires_at < datetime.utcnow():
            return False

        return True

