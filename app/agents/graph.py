from langgraph.graph import StateGraph, END

from app.agents.nodes.conversation import generate_conversational_response
from app.agents.nodes.gather_user_info import gather_user_info
from app.agents.nodes.intent_classifier import classify_intent
from app.agents.state import AgentState
from app.agents.nodes.sql_query_generate_tool import generate_sql_query


def build_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("conversation", generate_conversational_response)
    workflow.add_node("gather_user_info", gather_user_info)
    workflow.add_node("generate_sql_query", generate_sql_query)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")
        if intent in ["calculate"]:
            return "gather_user_info"
        if intent in ["question"]:
            return "question"  #TODO: implement question node with RAG
        return "conversation"

    def route_after_gather_info(state: AgentState) -> str:
        missing_info = state.get("missing_info")
        print(f"Routing from gather_info: {missing_info}")
        if missing_info is False:
            return "generate_sql_query"
        else:
            return END

    workflow.set_entry_point("classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "conversation": "conversation",
            "gather_user_info": "gather_user_info",
            "question": "conversation"
        }
    )

    workflow.add_conditional_edges(
        "gather_user_info",
        route_after_gather_info,
        {
            "generate_sql_query": "generate_sql_query",
            "conversation": "conversation",
            END: END
        }
    )

    workflow.add_edge("generate_sql_query", END)

    return workflow.compile()