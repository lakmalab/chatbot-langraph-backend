from sqlalchemy.orm import Session as DBSession
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.graph import create_pension_agent
from app.agents.state import AgentState
from app.enums import RoleType, SchemeType
from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage

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

        conversation = self.get_or_create_conversation(
            session_id=session_id,
            conversation_id=conversation_id,
            scheme_type=scheme_type
        )
        history = self.get_conversation_history(conversation.id)

        self.save_message(
            conversation_id=conversation.id,
            role= RoleType.USER,
            content=user_message
        )

        initial_state: AgentState = {
            "messages": history + [HumanMessage(content=user_message)],
            "user_query": user_message,
            "session_id": session_id,
            "conversation_id": conversation.id,
            "intent": None,
            "current_age": None,
            "desired_pension": None,
            "calculation_result": None,
            "response": "",
            "next_action": None
        }

        result = await self.agent.ainvoke(initial_state)

        response_text = result.get("response", "I'm sorry, I couldn't process that.")
        intent = result.get("intent")

        self.save_message(
            conversation_id=conversation.id,
            role=RoleType.ASSISTANT,
            content=response_text,
            intent=intent
        )
        if result.get("calculation_result"):
            self.save_calculation(
                session_id=session_id,
                conversation_id=conversation.id,
                calculation_result=result["calculation_result"],
                current_age=result["current_age"],
                desired_pension=result["desired_pension"]
            )

        return {
            "conversation_id": conversation.id,
            "response": response_text,
            "intent": intent,
            "metadata": {
                "calculation_result": result.get("calculation_result")
            }
        }

    def get_or_create_conversation(self, session_id, conversation_id, scheme_type):
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.session_id == session_id
            ).first()

            if conversation:
                return conversation

        conversation = Conversation(
            session_id=session_id,
            title=f" AAIB Assistant - {scheme_type}"
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_conversation_history(self, conversation_id: int) -> list:
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).all()

        return [
            HumanMessage(content=msg.content) if msg.role == RoleType.USER else AIMessage(content=msg.content)
            for msg in messages
        ]

    def save_message(
            self,
            conversation_id: int,
            role: RoleType,
            content: str,
            intent: str = None,
            metadata: Dict[str, Any] = None
    ) -> ChatMessage:

        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            intent=intent,
            metadata=metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message