from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):

    messages: List[BaseMessage]
    user_query: str

    session_id: str
    conversation_id: Optional[int]
    intent: Optional[str]
    current_age: Optional[int]
    desired_pension: Optional[float]
    payment_method: Optional[str]

    missing_info: bool
    generated_sql: Optional[str]

    tool_results: str

    response: str
    next_action: Optional[str]