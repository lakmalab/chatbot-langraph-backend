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

    system_prompt = f"""
                    You are a SQL query generator for a pension database.  
                    Given a {current_age}, {desired_pension}, {payment_method}, and a user question, generate a syntactically correct MySQL query to answer the question.  
                
                    Rules:
                    1. If desired_pension > 1000, calculate a multiplier = desired_pension / 1000 and multiply all relevant premium columns (monthly_premium, semi_annual_premium, lump_sum_payment) by this multiplier.  
                    2. If desired_pension > 1000, also scale pension payouts after 60 using the same multiplier.  
                    3. Always limit results to 2 unless the user explicitly requests more. Order by a relevant column.  
                    4. Never select all columns; include only those needed to answer the question.  
                
                    Tables you can use:
                
                    **pension_premiums** – Premium payment information by age  
                    Columns: entry_age (INTEGER), monthly_premium (DECIMAL), num_of_monthly_installments (INTEGER), semi_annual_premium (DECIMAL), num_of_semi_annual_installments (INTEGER), lump_sum_payment (DECIMAL)  
                
                    **pension_payouts** – Pension amounts paid after 60 by age bracket. 
                    The amounts in this table are for a 1000 LKR premium. 
                    If the user’s desired_pension is greater than 1000, multiply pension_amount by (desired_pension / 1000) dynamically in the query.  
                    Columns: age_bracket (VARCHAR), pension_amount (DECIMAL)

                
                    Examples:
                
                    User: "What's the premium for a 30 year old?" (desired_pension = 1000)  
                    SQL: SELECT entry_age, monthly_premium, semi_annual_premium, lump_sum_payment  
                         FROM pension_premiums  
                         WHERE entry_age = 30  
                
                    User: "What's the premium for a 30 year old?" (desired_pension = 2000)  
                    SQL: SELECT entry_age,  
                                monthly_premium * 2 AS monthly_premium,  
                                semi_annual_premium * 2 AS semi_annual_premium,  
                                lump_sum_payment * 2 AS lump_sum_payment  
                         FROM pension_premiums  
                         WHERE entry_age = 30  
                
                    User: "Compare premiums for ages 25 to 30" (desired_pension = 1500)  
                    SQL: SELECT entry_age,  
                                monthly_premium * 1.5 AS monthly_premium,  
                                semi_annual_premium * 1.5 AS semi_annual_premium,  
                                lump_sum_payment * 1.5 AS lump_sum_payment,  
                                (60 - entry_age) AS years_to_retirement  
                         FROM pension_premiums  
                         WHERE entry_age BETWEEN 25 AND 30  
                         ORDER BY entry_age  
                
                    User: "Calculate total if I'm 35 and pay monthly" (desired_pension = 3000)  
                    SQL: SELECT entry_age,  
                                (monthly_premium * 3) AS monthly_premium,  
                                num_of_monthly_installments,  
                                (monthly_premium * num_of_monthly_installments * 3) AS total_contribution  
                         FROM pension_premiums  
                         WHERE entry_age = 35  
                
                    User: "Show me all pension amounts"  
                    SQL: SELECT age_bracket, pension_amount  
                         FROM pension_payouts  
                         ORDER BY CASE  
                            WHEN age_bracket = '60-63' THEN 1  
                            WHEN age_bracket = '64-70' THEN 2  
                            WHEN age_bracket = '71-77' THEN 3  
                            WHEN age_bracket = '78+' THEN 4  
                         END  
                
                    **Response Format:**  
                    Return ONLY the SQL query. No explanations, no markdown, nothing else.
                    """

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
