from app.agents.state import AgentState


def request_user_confirmation(state: AgentState) -> AgentState:

    params = state.get("query_params", {})

    print(f"[REQUEST_CONFIRMATION] Requesting confirmation with params: {params}")

    description = params.get("description", "a database query")

    confirmation_message = f"""
                            📋 **Let me confirm the details before I fetch the information:**
                            
                            {description}
                            
                            """

    if "age" in params:
        confirmation_message += f"👤 **Your Age:** {params['age']} years\n"

    if "desired_pension" in params:
        confirmation_message += f"💰 **Target Pension:** {params['desired_pension']} LKR per month\n"

    if "age_range" in params:
        confirmation_message += f"📊 **Age Range:** {params['age_range']}\n"

    confirmation_message += """
                            ✅ Would you like me to proceed with fetching this information?
                            
                            Please reply:
                            - **"Yes"** or **"Confirm"** to proceed
                            - **"No"** or **"Cancel"** to modify your request
                            """

    state["response"] = confirmation_message
    state["awaiting_confirmation"] = True
    state["user_confirmed"] = None

    print("[REQUEST_CONFIRMATION] Set awaiting_confirmation to True")

    return state