from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel
import json

def gather_user_info(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0.7, provider=AiModel.OPENAI)

    system_prompt = """
                    You are an information gatherer for a pension scheme chatbot.
                    Your goal is to collect the following information from the user:
                    1. current_age (or date of birth) — must be between 18 and 55 years.
                    2. desired_pension — monthly pension at age 60 (minimum 1000 rupees).
                    3. payment_method — must be one of: monthly, semi_annual, or lump_sum.
    
                    Rules:
                    - Check old messages (conversation context) to see if user already provided info.
                    - If missing or unclear, ask politely for it.
                    - Guide the user back on track if they go off-topic.
                    - Respond conversationally.
                    - Once all 3 details are gathered, say "Thank you, I have all the information I need."
                    - Once all 3 details are gathered, return a json with these fields:
                    {
                        "current_age": int or null,
                        "desired_pension": float or null,
                        "payment_method": "monthly", "semi_annual", "lump_sum", or null
                    }
                    """

    messages = [SystemMessage(content=system_prompt)]

    if "messages" in state:
        messages.extend(state["messages"])

    user_query = state.get("user_query")
    if user_query:
        messages.append(HumanMessage(content=user_query))

    ai_response = llm.invoke(messages)
    ai_text = ai_response.content.strip()
    messages.append(AIMessage(content=ai_text))

    extracted_json = None
    json_start = ai_text.find("{")
    json_end = ai_text.rfind("}") + 1
    if json_start != -1 and json_end != -1:
        extracted_json = ai_text[json_start:json_end]

    if extracted_json:
        try:
            parsed = json.loads(extracted_json)
            state["current_age"] = parsed.get("current_age", state.get("current_age"))
            state["desired_pension"] = parsed.get("desired_pension", state.get("desired_pension"))
            state["payment_method"] = parsed.get("payment_method", state.get("payment_method"))
        except json.JSONDecodeError:
            pass

    state["messages"] = messages

    if all([state.get("current_age"), state.get("desired_pension"), state.get("payment_method")]):
        state["missing_info"] = False
        state["response"] = "Thank you, I have all the information I need."
    else:
        state["missing_info"] = True
        state["response"] = ai_text

    return state