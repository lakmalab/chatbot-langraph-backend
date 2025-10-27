from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.enums import RoleType
from app.enums.scheme import SchemeType


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message content")
    session_id: str = Field(..., description="Unique session identifier")
    conversation_id: Optional[int] = Field(None, description="Conversation ID if continuing existing conversation")
    scheme_type: SchemeType = Field(default=SchemeType.PENSION, description="Type of pension scheme")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I need 1000 pension",
                "session_id": "user_123",
                "conversation_id": 1,
                "scheme_type": "PENSION"
            }
        }


class AbortRequest(BaseModel):
    session_id: str
    conversation_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    conversation_id: int
    response: str
    intent: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "response": "Here's your pension information...",
                "intent": "database",
                "metadata": {
                    "awaiting_confirmation": True,
                    "query_params": {
                        "age": 27,
                        "desired_pension": 1000
                    }
                }
            }
        }


class ConversationResponse(BaseModel):
    id: int
    session_id: str
    scheme_id: Optional[int]
    title: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageHistory(BaseModel):
    id: int
    role: RoleType
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
