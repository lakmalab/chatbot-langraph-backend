from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState


def get_context(state: AgentState):
    messages = state.get("messages", [])
    recent_context = []
    user_query = state.get("user_query", "")

    # take the last 4 messages for context
    for msg in messages[-4:]:
        role = "User" if msg.type == "human" else "Assistant"
        recent_context.append(f"{role}: {msg.content}")

    context_str = "\n".join(recent_context)

    return f"Conversation:\n{context_str}\n\nUser's latest message:\n{user_query}"