from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.state import AgentState


class getContextMemory:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history",
                                               return_messages=True,
                                               output_key="response")

    def add_message(self, role: str, content: str):
        if role.lower() == "user":
            self.memory.save_context({"input": content}, {"response": ""})
        elif role.lower() == "assistant":
            self.memory.save_context({"input": ""}, {"response": content})

    def get_history(self, limit: int = None):
        variables = self.memory.load_memory_variables(inputs={})
        messages = variables.get("chat_history", [])

        if limit is not None:
            messages = messages[-limit:]

        converted = []
        for msg in messages:
            if msg.type == "human":
                converted.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                converted.append(AIMessage(content=msg.content))
        return converted

