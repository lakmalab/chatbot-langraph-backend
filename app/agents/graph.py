from langgraph.graph import StateGraph, END

from app.agents.llm_provider import get_llm
from app.agents.nodes.conversation import generate_conversational_response
from app.agents.nodes.intent_classifier import classify_intent
from app.agents.state import AgentState
from app.enums import AiModel
from app.agents.tools import dynamic_sql_tool

def build_graph(db):


    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("conversation",generate_conversational_response )

    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", END)



    return workflow.compile()