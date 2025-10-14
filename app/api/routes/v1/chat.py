from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.db.connection import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.service.chat_service import ChatService
from app.service.session_service import SessionService

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


@router.get("/history/{conversation_id}")
async def get_chat_history(
        conversation_id: int,
        db: DBSession = Depends(get_db)
):
    from app.models.chat_message import ChatMessage

    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at).all()

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