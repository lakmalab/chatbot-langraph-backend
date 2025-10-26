from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
import json

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel


def generate_sql_query(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")

    messages_for_llm = conversation_history.copy()
    messages_for_llm.append(HumanMessage(content=user_message))

    system_prompt = """
    You are an expert SQL query generator for a pension database.
    Your job is to:
    1. Extract the key parameters from the user's question
    2. Create a syntactically correct MySQL query

    Return a JSON object with:
    - "sql_query": the SQL query string
    - "parameters": object describing what will be queried in plain language

    ---
    ## Tables:
    1. **pension_premiums**
       Columns:
         - entry_age (INTEGER)
         - monthly_premium (DECIMAL)
         - num_of_monthly_installments (INTEGER)
         - semi_annual_premium (DECIMAL)
         - num_of_semi_annual_installments (INTEGER)
         - lump_sum_payment (DECIMAL)

    2. **pension_payouts**
       Columns:
         - age_bracket (VARCHAR)
         - pension_amount (DECIMAL)
       Note: pension_amount values are for a 1000 LKR premium.

    ---
    ## Rules:
    1. If the user's query implies a pension amount (e.g., "for 2000 LKR pension"), 
       calculate multiplier = desired_pension / 1000 and scale numeric columns accordingly.
    2. If the user mentions an age, include it in a WHERE clause.
    3. Always limit results to 2 rows unless explicitly requested more.
    4. Order results logically.

    ---
    ## Output Format:
    Return ONLY valid JSON:
    {
      "sql_query": "SELECT ... FROM ... WHERE ...",
      "parameters": {
        "age": 30,
        "desired_pension": 2000,
        "query_type": "premium_calculation",
        "description": "Premium payments for a 30-year-old farmer wanting 2000 LKR pension"
      }
    }

    Examples of parameter descriptions:
    - "Premium payments for a 30-year-old farmer"
    - "Pension payout amounts for 2000 LKR monthly pension"
    - "Comparison of premiums between ages 25 and 35"
    """

    messages = ([SystemMessage(content=system_prompt), ] + messages_for_llm)

    response = llm.invoke(messages)

    try:
        result = json.loads(response.content.strip())
        query = result.get("sql_query", "").strip()
        params = result.get("parameters", {})

        state["generated_sql"] = query
        state["query_params"] = params
        state["awaiting_confirmation"] = True

        print(f"Generated SQL: {query}")
        print(f"Extracted Parameters: {params}")

    except json.JSONDecodeError:
        query = response.content.strip()
        state["generated_sql"] = query
        state["query_params"] = {"description": "Database query based on your request"}
        state["awaiting_confirmation"] = True
        print(f"Generated SQL (fallback): {query}")

    return state