from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.intent_classifier import classify_intent
from app.agents.nodes.parameter_extractor import extract_parameters
from app.agents.nodes.tool_caller import call_tools
from app.agents.nodes.response_generator import generate_response


def create_pension_agent(db):

    from app.agents.tools import pension_tools

    pension_tools.set_db_session(db)

    tools = [
        pension_tools.get_available_plans,
        pension_tools.calculate_premium_by_age,
        pension_tools.get_pension_for_premium,
        pension_tools.compare_plans_for_age
    ]

    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_parameters", extract_parameters)
    workflow.add_node("call_tools", lambda state: call_tools(state, tools))
    workflow.add_node("generate_response", generate_response)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")

        if intent in ["calculate", "compare", "question"]:
            return "extract_parameters"
        else:
            return "generate_response"

    def route_after_extraction(state: AgentState) -> str:
        intent = state.get("intent")

        if intent in ["calculate", "compare", "question"]:
            return "call_tools"
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
            "call_tools": "call_tools",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("call_tools", "generate_response")
    workflow.add_edge("generate_response", END)

    app = workflow.compile()
    #graph_image = app.get_graph().draw_png()
    #graph_image.save("agent_workflow.png")

    return app