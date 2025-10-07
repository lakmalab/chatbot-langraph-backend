from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.state import AgentState
from app.core.config import settings
import json


def extract_parameters(state: AgentState) -> AgentState:
    """
    Extract age and desired pension amount from user message
    """

    llm = ChatOpenAI(
        model=settings.OPENAI_AI_MODEL,
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY
    )

    conversation_context = "\n".join([msg.content for msg in state["messages"][-5:]])

    system_prompt = """You are a parameter extractor for a pension calculator.

                    Extract these values from the user's message:
                    1. current_age: User's current age (must be between 18-59)
                    2. desired_pension: Monthly pension amount they want at age 60
                    
                    Return a JSON object with these fields. If a value is not found, use null.
                    
                    Example user message: "I am 35 years old and want 50000 rupees pension"
                    Response: {"current_age": 35, "desired_pension": 50000}
                    
                    Example user message: "I want pension of 30k per month"
                    Response: {"current_age": null, "desired_pension": 30000}
                    
                    User message: """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Conversation context:\n{conversation_context}\n\nCurrent message: {state['user_query']}")
    ]

    response = llm.invoke(messages)

    try:
        params = json.loads(response.content)

        if params.get("current_age"):
            state["current_age"] = int(params["current_age"])

        if params.get("desired_pension"):
            # Handle "k" notation (e.g., 50k = 50000)
            pension_str = str(params["desired_pension"])
            if isinstance(params["desired_pension"], str) and "k" in pension_str.lower():
                pension_str = pension_str.lower().replace("k", "")
                state["desired_pension"] = float(pension_str) * 1000
            else:
                state["desired_pension"] = float(params["desired_pension"])

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error extracting parameters: {e}")
        pass

    return state