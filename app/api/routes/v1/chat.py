import logging


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic_core._pydantic_core import ValidationError
from app.enums import SchemeType
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, MessageHistory, AbortRequest

from app.service.chat_service import ChatService
from app.service.session_service import SessionService, get_session_service
from app.service.chat_service import get_chat_service


router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

logger = logging.getLogger(__name__)
@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
        request: ChatMessageRequest,
        chat_service: ChatService = Depends(get_chat_service)
):

    try:
        logger.info(f"Received message request: session={request.session_id}, conv={request.conversation_id}")
        logger.debug(f"Message content: {request.message[:100]}...")

        try:
            scheme = SchemeType[request.scheme_type.upper()] if request.scheme_type else SchemeType.PENSION
        except KeyError:
            scheme = SchemeType.PENSION
            logger.warning(f"Invalid scheme type '{request.scheme_type}', defaulting to PENSION")

        result = await chat_service.process_message(
            session_id=request.session_id,
            user_message=request.message,
            conversation_id=request.conversation_id,
            scheme_type=scheme
        )

        logger.info(f"Message processed successfully: conv={result['conversation_id']}")

        return ChatMessageResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            intent=result.get("intent"),
            metadata=result.get("metadata", {})
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/history/{conversation_id}")
async def get_chat_history(
        conversation_id: int,
        chat_service: ChatService = Depends(get_chat_service),
):

    return await chat_service.get_chat_history(conversation_id=conversation_id)

@router.post("/abort")
async def abort_conversation(
        request: AbortRequest,
        chat_service: ChatService = Depends(get_chat_service),
):
    result = await chat_service.abort_conversation(
        session_id=request.session_id,
        conversation_id=request.conversation_id,
    )
    return result


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