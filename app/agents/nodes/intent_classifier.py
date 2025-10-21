from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.get_context import getContextMemory
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel
import json


def classify_intent(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0.2, provider=AiModel.OPENAI)

    user_message = state.get("user_query", "")
    episodic_memory = state.get("episodic_memory")
    episodic_memory.add_message("user", user_message)
    messages_for_llm = episodic_memory.get_history(limit=20)

    system_prompt = """
    You are an intelligent intent classifier for a Farmers Pension Chatbot.

    You must analyze the **entire conversation context** and **the latest user message**
    to determine the correct intent.

    You understand when a user asks a **follow-up question** (without restating details),
    and you infer what they mean based on the previous topic.

    Return ONLY one of the following intents:

    - "greeting" → If the user greets or starts a new conversation.
    - "database" → If the user asks for pension calculation, premium, or payment info.
                    Tables database has:
                    **pension_premiums** – Premium payment information by age  
                    Columns: entry_age (INTEGER), monthly_premium (DECIMAL), num_of_monthly_installments (INTEGER), semi_annual_premium (DECIMAL), 
                    num_of_semi_annual_installments (INTEGER), lump_sum_payment (DECIMAL)  
                
    - "question" → If the user asks for information, rules, eligibility, or general queries.
    - "other" → If it doesn’t fit the above categories.

    Examples:
    - "Hello" → greeting
    - "How much should I pay for 5000 pension?" → database
    - "Can I join after age 55?" → question
    - "And what if I stop paying?" (after discussing pension) → question (follow-up)
    - "Tell me about benefits" → question
    - "What’s the premium?" → database
    """

    messages = [
        SystemMessage(content=system_prompt),
        *messages_for_llm,
        HumanMessage(content='Return output ONLY as valid JSON in this format: {"intent": "intent_name"}')
    ]

    response = llm.invoke(messages)
    print("now intent", response)
    try:
        result = json.loads(response.content)
        intent = result.get("intent", "other").strip().lower()
    except Exception:
        intent = "other"

    state["intent"] = intent

    print(f"[IntentClassifier] detected intent: {intent}")

    return state
