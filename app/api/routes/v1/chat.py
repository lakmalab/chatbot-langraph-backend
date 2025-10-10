from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.db.connection import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.service.chat_service import ChatService
from app.service.session_service import SessionService, get_session_service

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
        request: ChatMessageRequest,
        chat_service: ChatService = Depends(ChatService),
        session_service: SessionService = Depends(get_session_service)
):
    if not session_service.is_session_valid(request.session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    result = await chat_service.process_message(
        session_id=request.session_id,
        user_message=request.message,
        conversation_id=request.conversation_id,
        scheme_type=request.scheme_type
    )

    return ChatMessageResponse(**result)


