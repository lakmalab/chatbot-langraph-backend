from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm_provider import get_llm
from agents.state import AgentState
from core.config import settings
from enums import AiModel


def generate_response(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0.7, provider=AiModel.OPENAI)

    intent = state.get("intent")


    if intent == "greeting":
        state["response"] = """Hello! Welcome to the Agricultural and Agrarian Insurance Board Pension Scheme chatbot. 

I can help you with:
📊 Calculate your required monthly pension contribution
❓ Answer questions about the pension scheme
💰 Understand benefits and eligibility

How can I assist you today?"""
        return state

    if state.get("calculation_result"):
        result = state["calculation_result"]

        state["response"] = f"""✅ **Pension Calculation Results**

Based on your information:
- Current Age: {state['current_age']} years
- Desired Monthly Pension at 60: Rs. {result['expected_pension']:,.2f}

**Required Contribution:**
- Monthly Contribution: Rs. {result['monthly_contribution']:,.2f}
- Years Until Retirement: {result['years_to_retirement']} years
- Total Contribution: Rs. {result['total_contribution']:,.2f}

💡 By contributing Rs. {result['monthly_contribution']:,.2f} every month for the next {result['years_to_retirement']} years, you will receive Rs. {result['expected_pension']:,.2f} per month starting at age 60!

Would you like to:
- Try a different pension amount?
- Learn more about the scheme?
- Ask any questions?"""
        return state

    if state.get("next_action") == "ask_for_parameters":
        missing = []
        if not state.get("current_age"):
            missing.append("your current age")
        if not state.get("desired_pension"):
            missing.append("your desired monthly pension amount")

        state["response"] = f"""To calculate your pension contribution, I need {' and '.join(missing)}.

Please provide:
{chr(10).join([f'- {item}' for item in missing])}

Example: "I am 35 years old and want 50,000 rupees monthly pension" """
        return state

    if intent == "question":
        system_prompt = """You are a helpful assistant for the Agricultural and Agrarian Insurance Board Pension Scheme.

Answer questions about:
- Eligibility (farmers aged 18-59 can join)
- Retirement age (60 years)
- Benefits (monthly pension after retirement)
- Contribution requirements

Be concise and helpful. If you don't know, admit it."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_query"])
        ]

        response = llm.invoke(messages)
        state["response"] = response.content
        return state

    if intent == "unclear":
        state["response"] = """I'm not sure I understood that correctly. 

I can help you with:
1. **Calculate pension** - Tell me your age and desired pension amount
2. **Ask questions** - About the scheme, eligibility, benefits, etc.

What would you like to do?"""
        return state

    return state