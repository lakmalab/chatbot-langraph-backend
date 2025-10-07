from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from db.connection import get_db
from schemas.chat import ChatMessageRequest, ChatMessageResponse
from service.chat_service import ChatService
from service.session_service import SessionService

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
        request: ChatMessageRequest,
        db: DBSession = Depends(get_db)
):

    session_service = SessionService(db)
    if not session_service.is_session_valid(request.session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    chat_service = ChatService(db)
    result = await chat_service.process_message(
        session_id=request.session_id,
        user_message=request.message,
        conversation_id=request.conversation_id,
        scheme_type=request.scheme_type
    )

    return ChatMessageResponse(**result)


