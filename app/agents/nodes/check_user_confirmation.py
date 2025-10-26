from app.agents.state import AgentState
import re


def check_user_confirmation(state: AgentState) -> AgentState:
    user_message = state.get("user_query", "").lower().strip()

    print(f"[CHECK_CONFIRMATION] Checking user message: '{user_message}'")
    print(f"[CHECK_CONFIRMATION] Current awaiting_confirmation: {state.get('awaiting_confirmation')}")

    positive_patterns = [
        r'\b(yes|yeah|yep|yup|sure|ok|okay|confirm|proceed|go ahead|correct|right)\b',
        r'^y$',  # Just "y"
        r'\b(හරි|ඔව්|එකග|සරි)\b'
    ]

    negative_patterns = [
        r'\b(no|nope|nah|cancel|stop|wait|not|don\'t|negative)\b',
        r'^n$',
        r'\b(එපා|නෑ)\b'
    ]

    is_positive = any(re.search(pattern, user_message) for pattern in positive_patterns)
    is_negative = any(re.search(pattern, user_message) for pattern in negative_patterns)

    print(f"[CHECK_CONFIRMATION] is_positive: {is_positive}, is_negative: {is_negative}")

    if is_positive and not is_negative:
        state["user_confirmed"] = True
        state["awaiting_confirmation"] = False
        print("[CHECK_CONFIRMATION] User CONFIRMED - proceeding to SQL execution")

    elif is_negative:
        state["user_confirmed"] = False
        state["awaiting_confirmation"] = False
        state["response"] = """
                            🙏 No problem! 
                            
                            I won't proceed with that query. Please let me know:
                            - Would you like to modify your request?
                            - Or ask me something else?
                            
                            I'm here to help! 😊
                            """
        print("[CHECK_CONFIRMATION] User CANCELLED")

    else:
        state["user_confirmed"] = None
        state["awaiting_confirmation"] = True
        state["response"] = """
                            I didn't quite understand your response. 🤔
                            
                            Could you please confirm:
                            - Say **"Yes"** to proceed with the query
                            - Say **"No"** to cancel and modify your request
                            """
        print("[CHECK_CONFIRMATION] Ambiguous response - asking again")

    return state