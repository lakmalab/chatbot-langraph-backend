import asyncio
from datetime import datetime

from sqlalchemy.orm import Session as DBSession
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import Depends

from app.db.connection import get_db
from app.enums import SchemeType
from app.enums.role import RoleType
from app.models import Session
from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage
from app.agents.graph import build_graph
from app.agents.state import AgentState
from typing import Dict, Any, Optional
from langsmith import traceable


class ChatService:
    _shared_agent = None

    def __init__(self, db: DBSession):
        self.db = db
        if ChatService._shared_agent is None:
            ChatService._shared_agent = build_graph()
        self.agent = ChatService._shared_agent

    def get_or_create_conversation(
            self,
            session_id: str,
            scheme_type: SchemeType,
            conversation_id: Optional[int] = None
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
            scheme_type: SchemeType = SchemeType.PENSION
    ) -> Dict[str, Any]:

        conversation = self.get_or_create_conversation(
            session_id=session_id,
            conversation_id=conversation_id,
            scheme_type=scheme_type
        )

        mysql_history = self.get_conversation_history(conversation.id)
        recent_history = mysql_history[-10:] if len(mysql_history) > 10 else mysql_history

        thread_config = {
            "configurable": {
                "thread_id": f"{session_id}_conv_{conversation.id}"
            }
        }

        has_existing_state = False
        try:
            current_state = self.agent.get_state(thread_config)
            if current_state and hasattr(current_state, 'values') and current_state.values:
                has_existing_state = True
                print(f"[ChatService] Existing state found")
                print(
                    f"[ChatService] awaiting_confirmation: {current_state.values.get('awaiting_confirmation', False)}")
            else:
                print(f"[ChatService] No state values found")
        except Exception as e:
            print(f"[ChatService] No existing state: {e}")
            has_existing_state = False

        self.save_message(
            conversation_id=conversation.id,
            role=RoleType.USER,
            content=user_message
        )


        input_state = {
            "user_query": user_message,
            "session_id": session_id,
            "conversation_id": conversation.id,
            "messages": recent_history,
        }

        if not has_existing_state:
            input_state.update({
                "intent": None,
                "generated_sql": None,
                "tool_results": "",
                "missing_info": False,
                "response": "",
                "user_abort": False,
                "awaiting_confirmation": False,
                "user_confirmed": None,
                "query_params": None,
            })
            print("[ChatService] Initializing new conversation state")
        else:
            print("[ChatService] Using existing state, only updating user_query and messages")

        result = await self.agent.ainvoke(input_state, config=thread_config)

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
                "tool_results": result.get("tool_results"),
                "awaiting_confirmation": result.get("awaiting_confirmation", False),
                "query_params": result.get("query_params"),
                "user_confirmed": result.get("user_confirmed")
            }
        }

    async def add_new_conversation(self, session_id):

        new_conversation = Conversation(
            session_id=session_id,
            title="New Conversation"
        )
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)

        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.updated_at.desc()).all()
        conversations_object = {
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

        return conversations_object

    def _get_trace_url(self):
        return "https://smith.langchain.com"

    async def get_chat_history(self, conversation_id):
        messages = self.db.query(ChatMessage).filter(
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

    async def get_user_conversations(self, session_id):
        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.updated_at.desc()).all()
        conversations_object = {
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

        return conversations_object

    async def abort_conversation(self, session_id: str, conversation_id: int):
        thread_config = {
            "configurable": {
                "thread_id": f"{session_id}_conv_{conversation_id}"
            }
        }

        agent_state = {
            "user_abort": True
        }

        await self.agent.ainvoke(agent_state, config=thread_config)

        self.save_message(
            conversation_id=conversation_id,
            role=RoleType.USER,
            content="User aborted the conversation"
        )

        return "aborted"


def get_chat_service(db: DBSession = Depends(get_db)) -> ChatService:
    return ChatService(db)