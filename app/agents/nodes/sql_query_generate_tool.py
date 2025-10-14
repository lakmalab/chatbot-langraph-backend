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
                        Given a {current_age}, {desired_pension}, {payment_method}, and a user input question, 
                        create a syntactically correct MySQL query to help find the answer. 

                        If the desired pension amount is greater than 1000, calculate a multiplier as (desired_pension / 1000)
                        and multiply the premium columns (monthly_premium, semi_annual_premium, lump_sum_payment)
                        by that multiplier in the SQL query output.

                        Unless the user specifies a specific number of examples they wish to obtain,
                        always limit your query to at most 2 results. You can order results by a relevant column.

                        Never query for all the columns from a specific table — only include those needed for the question.

                        Only use the following tables:

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

                        **Examples:**

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
                        Return ONLY the SQL query, nothing else. No explanations, no markdown, just the query.
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
