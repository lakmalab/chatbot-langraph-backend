# app/agents/graph.py
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState

def create_pension_agent(db):

    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_parameters", extract_parameters)
    workflow.add_node("gather_information", gather_information)
    workflow.add_node("call_tool", call_pension_tool)
    workflow.add_node("generate_response", generate_conversational_response)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")
        if intent in ["calculate", "compare", "question"]:
            return "extract_parameters"
        return "generate_response"

    def route_after_gathering(state: AgentState) -> str:
        next_action = state.get("next_action")
        if next_action == "call_tool":
            return "call_tool"
        return "generate_response"

    workflow.set_entry_point("classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "extract_parameters": "extract_parameters",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("extract_parameters", "gather_information")

    workflow.add_conditional_edges(
        "gather_information",
        route_after_gathering,
        {
            "call_tool": "call_tool",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("call_tool", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()