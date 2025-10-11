from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
import json
from app.enums import AiModel


def generate_conversational_response(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    intent = state.get("intent")

    if intent == "greeting":
        state["response"] ="""
                            Hello! 🙏 Welcome to the Farmers Pension Scheme.
                            
                            I'm here to help you understand and calculate your pension benefits.
                            
                            I can help you:
                            ✅ Calculate required premium payments based on your age
                            ✅ Show pension amounts you'll receive at different ages
                            ✅ Answer questions about eligibility, rules, and benefits
                            
                            1️⃣ Your current age (must be between 18–55)  
                            2️⃣ The monthly pension amount you’d like to receive at age 60  
                            3️⃣ Confirmation that you are:  
                             🇱🇰 A Sri Lankan citizen  
                             👨‍🌾 A farmer by profession  
                            
                            What's would like me to help you with today?
                            """

        return state

    system_prompt = """
                    You are a friendly, conversational pension advisor for farmers.
                        **Guidelines:**
                        1. Start with a friendly acknowledgment
                        2. Use emojis sparingly (💰, ✅, 📊) to highlight key points
                        3. Be encouraging about retirement planning
                    
                    **Tone:** Warm, supportive, clear - like a helpful advisor talking to a farmer planning their future.
                    """

    messages = [
        SystemMessage(content=system_prompt),
    ]

    response = llm.invoke(messages)
    state["response"] = response.content