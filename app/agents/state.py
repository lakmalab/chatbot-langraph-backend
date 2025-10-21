from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):

    messages: List[BaseMessage]
    user_query: str

    session_id: str
    conversation_id: Optional[int]
    intent: Optional[str]

    missing_info: bool
    generated_sql: Optional[str]
    episodic_memory: Any
    tool_results: str

    response: str