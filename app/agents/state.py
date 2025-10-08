# app/agents/state.py
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for the pension chatbot agent"""

    # Conversation
    messages: List[BaseMessage]
    user_query: str

    # Session info
    session_id: str
    conversation_id: Optional[int]

    # Intent classification
    intent: Optional[str]  # 'calculate', 'question', 'greeting', 'unclear', 'compare'

    # Pension calculation data
    current_age: Optional[int]
    desired_pension: Optional[float]
    monthly_premium: Optional[float]
    calculation_result: Optional[dict]

    # Tool execution
    tool_results: Optional[List[Dict[str, Any]]]

    # Response
    response: str
    next_action: Optional[str]