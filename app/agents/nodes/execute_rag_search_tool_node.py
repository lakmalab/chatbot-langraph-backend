# app/agents/nodes/execute_rag_search_tool_node.py
from app.agents.state import AgentState
from app.agents.tools.rag_search_tool import rag_search_tool

def execute_rag(state: AgentState) -> AgentState:
    question = state.get("user_query")

    result = rag_search_tool(question)

    state["tool_results"] = result
   # state["response"] = result

    print(f"RAG Execution Results: {result}")
    return state
