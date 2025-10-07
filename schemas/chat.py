from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from enums.scheme import SchemeType


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str
    conversation_id: Optional[int] = None
    scheme_type: SchemeType
    #scheme_type: SchemeType = SchemeType.PENSION


class ChatMessageResponse(BaseModel):
    conversation_id: int
    response: str
    intent: Optional[str] = None
    metadata: Optional[dict] = None


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
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

