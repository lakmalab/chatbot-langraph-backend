from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.get_context import getContextMemory
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel


def generate_sql_query(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    user_message = state.get("user_query", "")

    episodic_memory = state.get("episodic_memory")
    episodic_memory.add_message("user", user_message)
    messages_for_llm = episodic_memory.get_history(limit=10)

    system_prompt = """
    You are an expert SQL query generator for a pension database.
    Your job is to create a syntactically correct MySQL query that best answers the user's question,
    using the available tables and following the rules below.

    ---
    ## Tables:
    1. **pension_premiums**
       #you need to get atleast entry age from user to generate query from here
       Columns:
         - entry_age (INTEGER)
         - monthly_premium (DECIMAL)
         - num_of_monthly_installments (INTEGER)
         - semi_annual_premium (DECIMAL)
         - num_of_semi_annual_installments (INTEGER)
         - lump_sum_payment (DECIMAL)

    2. **pension_payouts**
        #this table has payout pension amounts that are payed after 60,
       Columns:
         - age_bracket (VARCHAR)
         - pension_amount (DECIMAL)
       Note: pension_amount values are for a 1000 LKR premium .

    ---
    ## Rules:
    1. If the user's query implies a pension amount (e.g., “for 2000 LKR pension”), 
       calculate multiplier = desired_pension / 1000 and scale numeric columns accordingly.
       Example:
         pension_amount * (desired_pension / 1000)
         monthly_premium * (desired_pension / 1000)
    2. If the user mentions an age, include it in a WHERE clause (e.g., WHERE entry_age = 30).
    3. Always limit results to 2 rows unless explicitly requested more.
    4. Order results logically, e.g., by entry_age or age_bracket.
    5. Do NOT explain anything or include markdown — return ONLY the SQL query string.

    ---
    ## Examples

    User: "What’s the premium for a 30-year-old?"
    → SELECT entry_age, monthly_premium, semi_annual_premium, lump_sum_payment
      FROM pension_premiums
      WHERE entry_age = 30;

    User: "What’s the pension payout if I want 2000 LKR?"
    → SELECT age_bracket, pension_amount * 2 AS pension_amount
      FROM pension_payouts
      ORDER BY age_bracket;

    User: "Compare premiums from 25 to 35"
    → SELECT entry_age, monthly_premium, semi_annual_premium, lump_sum_payment
      FROM pension_premiums
      WHERE entry_age BETWEEN 25 AND 35
      ORDER BY entry_age;

    ---
    ## Output Format:
    Output ONLY the valid SQL query (without markdown, quotes, or explanations).
    """
    messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm)

    response = llm.invoke(messages)
    query = response.content.strip()

    state["generated_sql"] = query
    state["response"] = query
    print("messages_for_llm:", messages_for_llm)
    print(f"Generated SQL: {query}")
    return state
