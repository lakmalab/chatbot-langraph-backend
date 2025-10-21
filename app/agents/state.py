from typing import TypedDict, List, Optional, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):

    messages: Annotated[List, add_messages]
    user_query: str

    session_id: str
    conversation_id: Optional[int]
    intent: Optional[str]

    missing_info: bool
    generated_sql: Optional[str]
    tool_results: str

    response: str