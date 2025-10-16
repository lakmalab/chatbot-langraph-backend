from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.db.connection import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, MessageHistory
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
        db: DBSession = Depends(get_db)
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at).all()

    print("get_chat_history called")
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "intent": msg.intent,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }
@router.get("/conversations/{session_id}")
async def get_user_conversations(
        session_id: str,
        db: DBSession = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.updated_at.desc()).all()

    return {
        "session_id": session_id,
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]
    }