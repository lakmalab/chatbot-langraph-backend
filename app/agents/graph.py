from langgraph.graph import StateGraph, END

from app.agents.nodes.conversation import generate_conversational_response
from app.agents.nodes.execute_rag_search_tool_node import execute_rag
from app.agents.nodes.execute_sql_tool_node import execute_sql_tool_node
from app.agents.nodes.intent_classifier import classify_intent
from app.agents.state import AgentState
from app.agents.nodes.sql_query_generate_tool import generate_sql_query
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("conversation", generate_conversational_response)
    workflow.add_node("generate_sql_query", generate_sql_query)
    workflow.add_node("execute_sql_tool_node", execute_sql_tool_node)
    workflow.add_node("execute_rag_search_tool_node", execute_rag)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")
        if intent in ["database"]:
            return "generate_sql_query"
        if intent in ["question"]:
            return "question"
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
            "generate_sql_query": "generate_sql_query",
            "question": "execute_rag_search_tool_node"
        }
    )

    workflow.add_edge("generate_sql_query", "execute_sql_tool_node")
    workflow.add_edge("execute_sql_tool_node", "conversation")
    workflow.add_edge("conversation", END)

    workflow.add_edge("execute_rag_search_tool_node", "conversation")
    workflow.add_edge("conversation", END)

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
