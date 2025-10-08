from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
from app.enums import AiModel


def classify_intent(state: AgentState) -> AgentState:
    """
    Classify user intent:
    - calculate: User wants to calculate pension
    - question: User has questions about the scheme
    - greeting: User is greeting
    - unclear: Intent is unclear
    """
    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    system_prompt = """You are an intent classifier for a pension scheme chatbot.

Classify the user's message into ONE of these categories:
- "calculate": User wants to calculate pension contribution or pension amount
- "question": User has questions about the pension scheme, rules, eligibility, etc.
- "greeting": User is greeting or introducing themselves
- "unclear": Intent is not clear

Respond with ONLY the category name, nothing else."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower()

    valid_intents = ["calculate", "question", "greeting", "unclear"]
    if intent not in valid_intents:
        intent = "unclear"

    state["intent"] = intent

    return state