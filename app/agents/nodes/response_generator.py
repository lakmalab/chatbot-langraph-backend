from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
import json

from app.enums import AiModel


def generate_response(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0.7, provider=AiModel.OPENAI)

    intent = state.get("intent")
    tool_results = state.get("tool_results", [])


    if intent == "greeting":
        state["response"] = """Hello! Welcome to the Agricultural and Agrarian Insurance Board Farmers Pension Scheme. 🌾

This scheme offers:
✅ Fixed monthly premiums starting from Rs. 27
✅ Guaranteed pension from age 60
✅ Higher pension amounts as you age (60-63, 64-70, 71-77, 78+ years)
✅ Entry age: 18 to 55 years

I can help you:
1. Calculate required premium based on your age and desired pension
2. Show available pension plans
3. Compare options for your age
4. Answer questions about the scheme

What would you like to know?"""
        return state


    if tool_results:
        system_prompt = """You are a helpful pension scheme assistant for farmers.

The scheme offers FIXED monthly premiums with GUARANTEED pension amounts.
Key features:
- Entry age: 18-55 years
- Pension starts at age 60
- Four pension periods: 60-63, 64-70, 71-77, 78+ (increasing amounts)
- Lower premium if you join younger

Format tool results clearly:
- Show monthly premium prominently
- Explain pension amounts for different age brackets
- Calculate total contribution (premium × 12 months × years)
- Be encouraging and helpful

Use rupee symbol (Rs.) and format numbers with commas for readability."""

        tool_results_text = json.dumps(tool_results, indent=2)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"User asked: {state['user_query']}\n\nTool results:\n{tool_results_text}\n\nGenerate a friendly, clear response:")
        ]

        response = llm.invoke(messages)
        state["response"] = response.content

        # Store calculation for database
        if tool_results and isinstance(tool_results[0], dict):
            result = tool_results[0]
            if "monthly_premium" in result and "error" not in result:
                state["calculation_result"] = result
                state["current_age"] = result.get("current_age")
                state["desired_pension"] = result.get("pension_breakdown", {}).get("60-63")

        return state

    # Handle unclear intent
    state["response"] = """I'm here to help with the Farmers Pension Scheme! 

I can assist you with:
1. **Calculate premium** - "I'm 30 years old and want 5000 pension"
2. **View plans** - "What plans are available?"
3. **Compare options** - "Compare plans for my age"
4. **Ask questions** - About eligibility, benefits, etc.

What would you like to know?"""

    return state