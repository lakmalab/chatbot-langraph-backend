from langchain_core.tools import tool
from sqlalchemy.orm import Session as DBSession
from app.models.pension_premium_plan import PensionPremiumPlan
from app.models.pension_payout import PensionPayout
from app.models.pension_entry_age import PensionEntryAge
from typing import Dict, Any

_db_session: DBSession = None


def set_db_session(db: DBSession):
    global _db_session
    _db_session = db

@tool
def calculate_premium_by_age(current_age: int, desired_pension: float) -> Dict[str, Any]:

    if current_age < 18 or current_age > 55:
        return {
            "error": "Age must be between 18 and 55 to join the scheme",
            "current_age": current_age
        }

    entry_data = _db_session.query(PensionEntryAge).filter(
        PensionEntryAge.entry_age == current_age
    ).first()

    if not entry_data:
        return {"error": f"No premium data found for age {current_age}"}



    return {
        "current_age": ,
        "years_to_retirement": ,
        "monthly_premium": ,
        "total_contribution": ,
        "pension_breakdown":,
        "note":"
    }
