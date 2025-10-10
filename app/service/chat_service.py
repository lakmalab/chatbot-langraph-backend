from sqlalchemy.orm import Session as DBSession
from langchain_core.messages import HumanMessage, AIMessage
from app.enums.role import RoleType
from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage
from app.agents.graph import create_pension_agent
from app.agents.state import AgentState
from typing import Dict, Any, Optional


class ChatService:
    def __init__(self, db: DBSession):
        self.db = db
        self.agent = create_pension_agent(db)

    def get_or_create_conversation(
            self,
            session_id: str,
            conversation_id: Optional[int] = None,
            scheme_type: str = "pension"
    ) -> Conversation:

        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.session_id == session_id
            ).first()

            if conversation:
                return conversation

        latest_conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.updated_at.desc()).first()

        if latest_conversation:
            return latest_conversation

        conversation = Conversation(
            session_id=session_id,
            title=f"Pension Chat - {scheme_type}"
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

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

    def get_conversation_history(self, conversation_id: int) -> list:

        messages = self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).all()

        langchain_messages = []
        for msg in messages:
            if msg.role == RoleType.USER:
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == RoleType.ASSISTANT:
                langchain_messages.append(AIMessage(content=msg.content))

        return langchain_messages

    async def process_message(
            self,
            session_id: str,
            user_message: str,
            conversation_id: Optional[int] = None,
            scheme_type: str = "pension"
    ) -> Dict[str, Any]:

        conversation = self.get_or_create_conversation(
            session_id=session_id,
            conversation_id=conversation_id,
            scheme_type=scheme_type
        )

        history = self.get_conversation_history(conversation.id)

        self.save_message(
            conversation_id=conversation.id,
            role=RoleType.USER,
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
            "monthly_premium": None,
            "calculation_result": None,
            "tool_results": None,
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

        return {
            "conversation_id": conversation.id,
            "response": response_text,
            "intent": intent,
            "metadata": {
                "calculation_result": result.get("calculation_result"),
                "tool_results": result.get("tool_results")
            }
        }