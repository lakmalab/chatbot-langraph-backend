from app.agents.state import AgentState
from app.utils.pension_calculator import PensionCalculator


def calculate_pension(state: AgentState) -> AgentState:
    """
    Calculate pension contribution using extracted parameters
    """

    calculator = PensionCalculator()

    # Check if we have required parameters
    if not state.get("current_age") or not state.get("desired_pension"):
        state["next_action"] = "ask_for_parameters"
        return state

    try:
        result = calculator.calculate_monthly_contribution(
            current_age=state["current_age"],
            desired_monthly_pension=state["desired_pension"]
        )

        state["calculation_result"] = result
        state["next_action"] = "show_results"

    except ValueError as e:
        state["response"] = f"Sorry, there was an error with your input: {str(e)}"
        state["next_action"] = "error"

    return state