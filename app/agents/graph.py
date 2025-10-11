from langgraph.graph import StateGraph, END

from app.agents.nodes.calculate_pention import gather_user_info
from app.agents.nodes.conversation import generate_conversational_response
from app.agents.nodes.intent_classifier import classify_intent
from app.agents.state import AgentState


def build_graph(db):

    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("conversation", generate_conversational_response)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")
        if intent in ["calculate"]:
            return "calculate_pention"
        if intent in ["question"]:
            return "question"
        return "conversation"

    workflow.set_entry_point("classify_intent")
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "conversation": "conversation",
        }
    )

    return workflow.compile()