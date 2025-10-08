# app/agents/nodes/intent_classifier.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
from app.enums import AiModel


def classify_intent(state: AgentState) -> AgentState:
    """
    Classify user intent:
    - calculate: User wants to calculate pension/premium
    - compare: User wants to compare plans
    - question: User has questions about the scheme
    - greeting: User is greeting
    - unclear: Intent is unclear
    """

    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    system_prompt = """You are an intent classifier for a pension scheme chatbot.

Classify the user's message into ONE of these categories:

- "calculate": User wants to calculate premium or pension amount
  Examples: "I'm 30 and want 5000 pension", "How much to pay for 10k pension?", "Calculate my premium"

- "compare": User wants to compare different plans or see options
  Examples: "Show me all options", "Compare plans", "What are my choices?", "Show plans for my age"

- "question": User has questions about the scheme, eligibility, rules, benefits
  Examples: "What is the eligibility?", "How does the scheme work?", "What pension will I get?"

- "greeting": User is greeting or starting conversation
  Examples: "Hello", "Hi", "Good morning"

- "unclear": Intent is not clear or out of scope

Respond with ONLY the category name, nothing else."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower()


    valid_intents = ["calculate", "compare", "question", "greeting", "unclear"]
    if intent not in valid_intents:
        intent = "unclear"

    state["intent"] = intent

    return state