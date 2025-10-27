from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.nodes.check_user_confirmation import check_user_confirmation
from app.agents.nodes.conversation import generate_conversational_response
from app.agents.nodes.execute_rag_search_tool_node import execute_rag
from app.agents.nodes.execute_sql_tool_node import execute_sql_tool_node
from app.agents.nodes.intent_classifier import classify_intent
from app.agents.nodes.request_user_confirmation import request_user_confirmation
from app.agents.nodes.sql_query_generate_tool import generate_sql_query
from app.agents.state import AgentState


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("conversation", generate_conversational_response)
    workflow.add_node("generate_sql_query", generate_sql_query)
    workflow.add_node("request_confirmation", request_user_confirmation)
    workflow.add_node("check_confirmation", check_user_confirmation)
    workflow.add_node("execute_sql_tool_node", execute_sql_tool_node)
    workflow.add_node("execute_rag_search_tool_node", execute_rag)

    def route_entry(state: AgentState) -> str:

        awaiting = state.get("awaiting_confirmation", False)
        print(f"[ROUTE_ENTRY] awaiting_confirmation: {awaiting}")

        if awaiting:
            print("[ROUTE_ENTRY] Routing to check_confirmation")
            return "check_confirmation"
        else:
            print("[ROUTE_ENTRY] Routing to classify_intent")
            return "classify_intent"

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")
        print(f"[ROUTE_AFTER_INTENT] intent: {intent}")

        if intent in ["database"]:
            return "generate_sql_query"
        if intent in ["question"]:
            return "question"
        return "conversation"

    def route_after_sql_generation(state: AgentState) -> str:
        print("[ROUTE_AFTER_SQL] Going to request_confirmation")
        return "request_confirmation"

    def route_after_confirmation_check(state: AgentState) -> str:
        user_confirmed = state.get("user_confirmed")
        print(f"[ROUTE_AFTER_CONFIRMATION] user_confirmed: {user_confirmed}")

        if user_confirmed is True:
            print("[ROUTE_AFTER_CONFIRMATION] Executing SQL")
            return "execute_sql"
        elif user_confirmed is False:
            print("[ROUTE_AFTER_CONFIRMATION] User cancelled")
            return "conversation"
        else:
            print("[ROUTE_AFTER_CONFIRMATION] Still waiting for clear response")
            return "end"

    workflow.set_conditional_entry_point(
        route_entry,
        {
            "check_confirmation": "check_confirmation",
            "classify_intent": "classify_intent"
        }
    )

    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "conversation": "conversation",
            "generate_sql_query": "generate_sql_query",
            "question": "execute_rag_search_tool_node"
        }
    )

    workflow.add_conditional_edges(
        "generate_sql_query",
        route_after_sql_generation,
        {
            "request_confirmation": "request_confirmation"
        }
    )

    workflow.add_edge("request_confirmation", END)

    workflow.add_conditional_edges(
        "check_confirmation",
        route_after_confirmation_check,
        {
            "execute_sql": "execute_sql_tool_node",
            "conversation": "conversation",
            "end": END
        }
    )

    workflow.add_edge("execute_sql_tool_node", "conversation")
    workflow.add_edge("conversation", END)

    workflow.add_edge("execute_rag_search_tool_node", "conversation")

    '''
        compiled_graph = workflow.compile()
        image_bytes = compiled_graph.get_graph().draw_mermaid_png()
        with open("agent_workflow_graph.png", "wb") as f:
            f.write(image_bytes)
        print("Graph saved as 'agent_workflow_graph.png'")
        from IPython.display import Image, display
        display(Image(image_bytes))
    '''
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)