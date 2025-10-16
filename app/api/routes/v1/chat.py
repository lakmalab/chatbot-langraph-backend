from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.db.connection import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, MessageHistory
from app.service import session_service
from app.service.chat_service import ChatService
from app.service.session_service import SessionService, get_session_service
from app.service.chat_service import get_chat_service
from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
        request: ChatMessageRequest,
        chat_service: ChatService = Depends(get_chat_service),
        session_service: SessionService = Depends(get_session_service),
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


@router.get("/history/{conversation_id}")
async def get_chat_history(
        conversation_id: int,
        chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_chat_history(conversation_id=conversation_id)


@router.get("/conversations/{session_id}")
async def get_user_conversations(
        session_id: str,
        chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_user_conversations(session_id=session_id)



@router.get("/conversations/new/{session_id}")
async def add_new_conversation(
        session_id: str,
        chat_service: ChatService = Depends(get_chat_service),
        session_service: SessionService = Depends(get_session_service),
):
    if not session_service.is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    result = await chat_service.add_new_conversation(
        session_id=session_id
    )

    return result