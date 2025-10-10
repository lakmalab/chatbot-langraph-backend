import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
import json

from app.enums import AiModel


def extract_parameters(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0, provider=AiModel.OPENAI)


    conversation_context = ""
    for msg in state["messages"]:
        role = "User" if msg.type == "human" else "Assistant"
        conversation_context += f"{role}: {msg.content}\n"

    system_prompt = """You are a parameter extractor for a pension calculator.

                        Extract these values from the ENTIRE conversation:
                        1. current_age: User's current age (must be between 18-55)
                        2. desired_pension: Monthly pension amount they want (e.g., 1000, 5000, 10000)
                        3. monthly_premium: Monthly premium amount they're asking about (e.g., 27, 270, 2700)
                        
                        IMPORTANT: 
                        - Look through the entire conversation history, not just the last message
                        - If the user mentioned their age or amounts earlier, use that information
                        - Handle variations: "50k" = 50000, "5k" = 5000, "Rs. 270" = 270
                        
                        Return a JSON object with these fields. If a value is not found, use null.
                        
                        Example 1:
                        User: "I am 30 years old"
                        Assistant: "What pension amount would you like?"
                        User: "I want 5000 monthly"
                        Response: {"current_age": 30, "desired_pension": 5000, "monthly_premium": null}
                        
                        Example 2:
                        User: "What pension will I get for Rs. 270 premium?"
                        Response: {"current_age": null, "desired_pension": null, "monthly_premium": 270}
                        
                        Example 3:
                        User: "I'm 25, show me options"
                        Response: {"current_age": 25, "desired_pension": null, "monthly_premium": null}
                        """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Conversation:\n{conversation_context}\n\nExtract parameters as JSON:")
    ]

    response = llm.invoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        params = json.loads(content)

        if params.get("current_age"):
            state["current_age"] = int(params["current_age"])

        if params.get("desired_pension"):
            pension_value = params["desired_pension"]
            if isinstance(pension_value, str):
                # Handle "k" notation
                if "k" in pension_value.lower():
                    pension_value = pension_value.lower().replace("k", "").replace(",", "")
                    state["desired_pension"] = float(pension_value) * 1000
                else:
                    state["desired_pension"] = float(pension_value.replace(",", ""))
            else:
                state["desired_pension"] = float(pension_value)

        if params.get("monthly_premium"):
            premium_value = params["monthly_premium"]
            if isinstance(premium_value, str):
                premium_value = premium_value.replace(",", "").replace("Rs.", "").replace("rs", "").strip()
            state["monthly_premium"] = float(premium_value)

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error extracting parameters: {e}")
        print(f"Response content: {response.content}")

    return state