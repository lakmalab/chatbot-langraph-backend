from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.get_context import getContextMemory
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel
import json


def generate_conversational_response(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.3, provider=AiModel.OPENAI)
    intent = state.get("intent")

    user_message = state.get("user_query", "")
    episodic_memory = state.get("episodic_memory")
    episodic_memory.add_message("user", user_message)
    messages_for_llm = episodic_memory.get_history(limit=10)
    print("messages_for_llm:", messages_for_llm)
    if intent == "greeting":
        state["response"] = """
        👋 Hello! Welcome to the **Farmers Pension Scheme**.

        I'm here to help you understand and calculate your pension benefits.

        I can help you:
        ✅ Calculate required premium payments based on your age  
        ✅ Show pension amounts you'll receive at different ages  
        ✅ Answer questions about eligibility, rules, and benefits  

        To begin, please share:
        1️⃣ Your current age (must be between 18–55)  
        2️⃣ The monthly pension amount you’d like to receive at age 60  
        3️⃣ Confirmation that you are:  
         🇱🇰 A Sri Lankan citizen  
         👨‍🌾 A farmer by profession  

        What would you like me to help you with today?
        """
        return state

    elif intent == "question":
        tool_response = state["tool_results"]

        system_prompt = """
        You are a friendly and knowledgeable pension advisor for farmers.

        🎯 **Goal:** Take the technical or factual answer from the tool and rephrase it 
        in a warm, conversational tone — easy to understand for a Sri Lankan farmer.

        ✅ Use short, simple sentences.  
        ✅ Use a few emojis (💰, 📊, ✅, 🙏) to make it engaging.  
        ✅ If numbers or benefits are mentioned, highlight them clearly.  
        ✅ Encourage the user positively about their pension planning.

        Example:
        Tool says: "The monthly premium is 350 LKR for 20 years."
        Response: "💰 You’ll just need to pay about **350 LKR per month** for 20 years — that’s a small step toward a secure pension at 60! 🙏"
        """
        messages = ([SystemMessage(content=system_prompt),] + messages_for_llm +
                    [HumanMessage(content=f"Tool response: {tool_response}")])

        response = llm.invoke(messages)
        state["response"] = response.content
        return state
    elif intent == "database":
        tool_response = state["tool_results"]

        system_prompt = """
        You are a **friendly and knowledgeable pension advisor** who helps **Sri Lankan farmers** understand their pension plans. 🇱🇰👨‍🌾  

        🎯 **Your Goal:**  
        Take the **technical or factual answer** from the tool (e.g., from the database) and **rephrase it in a warm, simple, and conversational tone** that any farmer can easily understand.

        If the tool gives an **error**, **incomplete**, or **unclear** result, kindly ask the user for the **necessary missing details** (like entry age) before proceeding to generate the correct database query.  

        ---

        ### 🗂️ **Database Reference**
        Here are the available tables and their columns for your context:

        1. **pension_premiums**  
           - Purpose: Holds premium payment details.  
           - You must get at least the **entry_age** from the user to query this table.  
           - **Columns:**  
             - entry_age (INTEGER)  
             - monthly_premium (DECIMAL)  
             - num_of_monthly_installments (INTEGER)  
             - semi_annual_premium (DECIMAL)  
             - num_of_semi_annual_installments (INTEGER)  
             - lump_sum_payment (DECIMAL)

        2. **pension_payouts**  
           - Purpose: Stores pension payout details for those aged 60 and above.  
           - **Columns:**  
             - age_bracket (VARCHAR)  
             - pension_amount (DECIMAL)  
           - **Note:** `pension_amount` values are calculated for a **1,000 LKR premium**.

        ---

        ### 💬 **Response Style Guidelines**
        ✅ Use **short, simple sentences**.  
        ✅ Be **friendly and motivational** — make the farmer feel confident.  
        ✅ Use a few **emojis** (💰📊✅🙏) to make the message engaging.  
        ✅ **Highlight important numbers and benefits** (use bold for clarity).  
        ✅ If data is missing, politely ask the user for it — don’t make assumptions.  

        ---

        ### 🧩 **Example Transformation**

        **Tool Output:**  
        > The monthly premium is 350 LKR for 20 years.

        **Your Response:**  
        > 💰 You’ll just need to pay about **350 LKR per month** for 20 years — that’s a small step toward a **secure pension at 60**! 🙏  

        ---

        Keep your tone **warm, trustworthy, and supportive**, like a local advisor helping farmers plan their future. 🌾
        """

        messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm +
                    [HumanMessage(content=f"Tool response: {tool_response}")])

        response = llm.invoke(messages)
        state["response"] = response.content
        return state

    else:
        system_prompt = """
            You are an intelligent intent classifier for a Farmers Pension Chatbot.

            You must analyze the **entire conversation context** and **the latest user message**
            to determine the correct intent.

            You understand when a user asks a **follow-up question** (without restating details),
            and you infer what they mean based on the previous topic. if latest user question goes outside oraganizational scope stire conversation toward it."""

        messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm)
        response = llm.invoke(messages)
        state["response"] = response.content
        return state
