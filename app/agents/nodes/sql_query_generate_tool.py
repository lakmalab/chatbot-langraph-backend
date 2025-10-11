from typing import Dict, Any
from langchain_core.tools import tool


from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.enums import AiModel

def generate_sql_query(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    current_age = state.get("current_age")
    desired_pension = state.get("desired_pension")
    payment_method = state.get("payment_method")

    system_prompt = f"""You are a SQL query generator for a pension database.
                    **Available Tables:**
                    
                    1. **pension_premiums** - Premium payment information by age
                       Columns:
                       - entry_age (INTEGER): Age when joining (18-55)
                       - monthly_premium (DECIMAL): Monthly payment amount
                       - num_of_monthly_installments (INTEGER): Number of monthly payments until age 60
                       - semi_annual_premium (DECIMAL): Semi-annual payment amount  
                       - num_of_semi_annual_installments (INTEGER): Number of semi-annual payments
                       - lump_sum_payment (DECIMAL): One-time payment amount
                    
                    2. **pension_payouts** - Pension amounts by age bracket
                       Columns:
                       - age_bracket (VARCHAR): Age range (e.g., '60-63', '64-70', '71-77', '78+')
                       - pension_amount (DECIMAL): Monthly pension amount
                    
                    **Your Task:**
                    use {current_age}, {desired_pension}, {payment_method} to
                    Generate a SQL SELECT query to answer the user's question.

                    **Examples:**
                    User: "What's the premium for a 30 year old?"
                    SQL: SELECT entry_age, monthly_premium, semi_annual_premium, lump_sum_payment FROM pension_premiums WHERE entry_age = 30
                    
                    User: "Show me all pension amounts"
                    SQL: SELECT age_bracket, pension_amount FROM pension_payouts ORDER BY CASE WHEN age_bracket = '60-63' THEN 1 WHEN age_bracket = '64-70' THEN 2 WHEN age_bracket = '71-77' THEN 3 WHEN age_bracket = '78+' THEN 4 END
                    
                    User: "Compare premiums for ages 25 to 30"
                    SQL: SELECT entry_age, monthly_premium, semi_annual_premium, (60 - entry_age) as years_to_retirement FROM pension_premiums WHERE entry_age BETWEEN 25 AND 30 ORDER BY entry_age
                    
                    User: "Calculate total if I'm 35 and pay monthly"
                    SQL: SELECT entry_age, monthly_premium, num_of_monthly_installments, (monthly_premium * num_of_monthly_installments) as total_contribution FROM pension_premiums WHERE entry_age = 35


                    **Response Format:**
                    Return ONLY the SQL query, nothing else. No explanations, no markdown, just the query."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    query = response.content.strip().lower()



    state["generated_sql"] = query
    state["response"] = query
    print(f"Generated SQL: {query}")
    return state