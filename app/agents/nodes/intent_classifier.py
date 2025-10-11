from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
from app.enums import AiModel


def classify_intent(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    system_prompt = """You are an intent classifier for a pension scheme chatbot.

                    Classify the user's message into ONE of these categories:
                     - "calculate": look at the last messages and if its about calculating pension give this category priority a User wants to calculate premium or pension amount
                      Examples: "I'm 30 and want 5000 pension", "How much to pay for 10k pension?", "i'm 27", "years old", "monthly", "semi_annual", "lump_sum",
                      "Calculate my premium"
                      
                     - "greeting": User is greeting or starting conversation
                      Examples: "Hello", "Hi", "Good morning"
                      
                    - "question": User has questions about the scheme, eligibility, rules, benefits
                      Examples: "What is the eligibility?", "How does the scheme work?", 
                      "What pension will I get?"
                    
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
    print(f"Classified intent: {intent}")
    return state
