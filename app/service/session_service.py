import uuid
from datetime import datetime, timedelta
from fastapi import Depends
from app.core.config import settings
from app.db.connection import get_db
from app.models import Conversation
from app.schemas.session import SessionCreate
from app.models.session import Session

class SessionService:
    def __init__(self, DBSession):
        self.db = DBSession

    def create_session(self, ip_address: str, user_agent: str) -> Session:
        existing_session = self.db.query(Session).filter(Session.ip_address == ip_address).order_by(Session.expires_at.desc()).first()
        existing_session = (
            self.db.query(Session)
            .filter(Session.ip_address == ip_address)
            .order_by(Session.expires_at.desc())
            .first()
        )

        if existing_session and existing_session.expires_at > datetime.utcnow():
            conversation = (
                self.db.query(Conversation)
                .filter(Conversation.session_id == existing_session.session_id)
                .first()
            )

            if not conversation:
                new_conversation = Conversation(
                    session_id=existing_session.session_id,
                    title="New Conversation"
                )
                self.db.add(new_conversation)
                self.db.commit()
                self.db.refresh(new_conversation)

            return existing_session

        session_data = SessionCreate(
            ip_address=ip_address,
            user_agent=user_agent
        )
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

        new_conversation = Conversation(
            session_id=new_session.session_id,
            title="New Conversation"
        )
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)

        return new_session

    def is_session_valid(self, session_id: str) -> bool:
        session = self.db.query(Session).filter(Session.session_id == session_id).first()
        if not session:
            return False
        if session.expires_at and session.expires_at < datetime.utcnow():
            return False
        return True

    @staticmethod
    def get_session_service(db: Session = Depends(get_db)):
        return SessionService(db)


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    return SessionService(db)
