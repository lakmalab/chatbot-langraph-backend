from langgraph.graph import StateGraph, END
from app.agents.state import AgentState

def create_agent(db):
    workflow = StateGraph(AgentState)


    return workflow.compile()
