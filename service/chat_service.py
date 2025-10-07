from sqlalchemy.orm import Session as DBSession
from langchain_core.messages import HumanMessage, AIMessage

from enums import RoleType, SchemeType
from models.conversation import Conversation
from models.chat_message import ChatMessage
from models.pension_calculation import PensionCalculation
from agents.graph import create_pension_agent
from agents.state import AgentState
from typing import Dict, Any


class ChatService:
    def __init__(self, db: DBSession):
        self.db = db
        self.agent = create_pension_agent()


    async def process_message(
            self,
            session_id: str,
            user_message: str,
            conversation_id: int = None,
            scheme_type:SchemeType= SchemeType.PENSION
    ) -> Dict[str, Any]:


        return {
            "conversation_id": conversation_id,
            "response": "hello"
        }