from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel
import json


def generate_conversational_response(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.3, provider=AiModel.OPENAI)
    intent = state.get("intent")

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")

    messages_for_llm = conversation_history.copy()
    messages_for_llm.append(HumanMessage(content=user_message))

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
        2️⃣ The monthly pension amount you'd like to receive at age 60  
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
        Response: "💰 You'll just need to pay about **350 LKR per month** for 20 years — that's a small step toward a secure pension at 60! 🙏"
        """
        messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm +
                    [HumanMessage(content=f"Tool response: {tool_response}")])

        response = llm.invoke(messages)
        state["response"] = response.content
        return state

    elif intent == "database":
        tool_response = state.get("tool_results", "")

        # Only generate response if we have tool results (query was executed)
        if not tool_response:
            # This shouldn't happen, but handle gracefully
            return state

        system_prompt = """
        You are a **friendly and knowledgeable pension advisor** who helps **Sri Lankan farmers** understand their pension plans. 🇱🇰👨‍🌾  

        🎯 **Your Goal:**  
        Take the **technical or factual answer** from the database query results and **rephrase it in a warm, simple, and conversational tone** that any farmer can easily understand.

        ---

        ### 🗂️ **Database Reference**
        Here are the available tables and their columns for your context:

        1. **pension_premiums**  
           - Purpose: Holds premium payment details.  
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
        ✅ Thank them for confirming and proceeding with the query.

        ---

        ### 🧩 **Example Transformation**

        **Tool Output:**  
        > The monthly premium is 350 LKR for 20 years.

        **Your Response:**  
        > 💰 Great news! You'll just need to pay about **350 LKR per month** for 20 years — that's a small step toward a **secure pension at 60**! 🙏  

        ---

        Keep your tone **warm, trustworthy, and supportive**, like a local advisor helping farmers plan their future. 🌾
        """

        messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm +
                    [HumanMessage(content=f"Database query results: {tool_response}")])

        response = llm.invoke(messages)
        state["response"] = response.content
        return state

    else:
        system_prompt = """
            You are an intelligent assistant for a Farmers Pension Chatbot.

            Analyze the conversation context and provide a helpful response.
            If the user's question is outside the scope of pension information,
            gently guide them back to pension-related topics.

            Keep your tone friendly and supportive."""

        messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm)
        response = llm.invoke(messages)
        state["response"] = response.content
        return state