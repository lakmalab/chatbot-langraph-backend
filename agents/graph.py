from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.intent_classifier import classify_intent
from agents.nodes.parameter_extractor import extract_parameters
from agents.nodes.calculator import calculate_pension
from agents.nodes.response_generator import generate_response


def create_pension_agent():

    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_parameters", extract_parameters)
    workflow.add_node("calculate", calculate_pension)
    workflow.add_node("generate_response", generate_response)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")

        if intent == "calculate":
            return "extract_parameters"
        else:
            return "generate_response"

    def route_after_extraction(state: AgentState) -> str:
        if state.get("current_age") and state.get("desired_pension"):
            return "calculate"
        else:
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

    workflow.add_conditional_edges(
        "extract_parameters",
        route_after_extraction,
        {
            "calculate": "calculate",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("calculate", "generate_response")
    workflow.add_edge("generate_response", END)

    app = workflow.compile()

    return app