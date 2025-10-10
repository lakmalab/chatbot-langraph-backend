from langchain_core.tools import tool
from sqlalchemy.orm import Session as DBSession
from app.models.pension_premium_plan import PensionPremiumPlan
from app.models.pension_payout import PensionPayout
from app.models.Pension_premium import PensionEntryAge
from typing import Dict, Any

_db_session: DBSession = None


def set_db_session(db: DBSession):
    global _db_session
    _db_session = db

@tool
def calculate_premium_by_age(current_age: int, desired_pension: float) -> Dict[str, Any]:
    """
    Calculate required monthly premium based on current age and desired pension at age 60-63.
    Use this when user provides their age and desired pension amount.

    Args:
        current_age: Current age of the person (18-55)
        desired_pension: Desired monthly pension amount at retirement (60-63 age bracket)

    Returns:
        Dictionary with required premium and pension details
    """
    # Validate age
    if current_age < 18 or current_age > 55:
        return {
            "error": "Age must be between 18 and 55 to join the scheme",
            "current_age": current_age
        }

    # Get entry age data
    entry_data = _db_session.query(PensionEntryAge).filter(
        PensionEntryAge.entry_age == current_age
    ).first()

    if not entry_data:
        return {"error": f"No premium data found for age {current_age}"}

    # Determine which premium bracket based on desired pension
    premium_options = [
        {"pension": 1000, "premium": float(entry_data.premium_for_1000)},
        {"pension": 2500, "premium": float(entry_data.premium_for_2500)},
        {"pension": 5000, "premium": float(entry_data.premium_for_5000)},
        {"pension": 10000, "premium": float(entry_data.premium_for_10000)},
    ]

    # Find closest matching pension amount
    closest_option = min(premium_options, key=lambda x: abs(x["pension"] - desired_pension))

    # Get full pension breakdown for this premium
    matching_plan = _db_session.query(PensionPremiumPlan).filter(
        PensionPremiumPlan.monthly_premium == closest_option["premium"]
    ).first()

    pension_breakdown = {}
    if matching_plan:
        payouts = _db_session.query(PensionPayout).filter(
            PensionPayout.plan_id == matching_plan.id
        ).all()
        pension_breakdown = {
            payout.age_bracket: float(payout.pension_amount)
            for payout in payouts
        }

    years_to_60 = entry_data.years_to_60
    total_contribution = closest_option["premium"] * 12 * years_to_60

    return {
        "current_age": current_age,
        "years_to_retirement": years_to_60,
        "monthly_premium": closest_option["premium"],
        "total_contribution": round(total_contribution, 2),
        "pension_breakdown": pension_breakdown,
        "note": f"Closest available pension plan for Rs.{desired_pension} is Rs.{closest_option['pension']}"
    }


@tool
def get_pension_for_premium(monthly_premium: float) -> Dict[str, Any]:
    """
    Get pension amounts for a specific monthly premium (e.g., Rs. 27, 270, 2700).
    Use this when user asks "what pension will I get for Rs. X premium?"

    Args:
        monthly_premium: Monthly premium amount (27, 270, or 2700)

    Returns:
        Dictionary with pension amounts for different age brackets
    """
    plan = _db_session.query(PensionPremiumPlan).filter(
        PensionPremiumPlan.monthly_premium == monthly_premium,
        PensionPremiumPlan.is_active == True
    ).first()

    if not plan:
        available_premiums = _db_session.query(PensionPremiumPlan.monthly_premium).filter(
            PensionPremiumPlan.is_active == True
        ).all()
        return {
            "error": f"No plan found for premium Rs.{monthly_premium}",
            "available_premiums": [float(p[0]) for p in available_premiums]
        }

    payouts = _db_session.query(PensionPayout).filter(
        PensionPayout.plan_id == plan.id
    ).all()

    return {
        "plan_name": plan.plan_name,
        "monthly_premium": float(plan.monthly_premium),
        "pension_amounts": {
            "age_60_63": float(next((p.pension_amount for p in payouts if p.age_bracket == "60-63"), 0)),
            "age_64_70": float(next((p.pension_amount for p in payouts if p.age_bracket == "64-70"), 0)),
            "age_71_77": float(next((p.pension_amount for p in payouts if p.age_bracket == "71-77"), 0)),
            "age_78_plus": float(next((p.pension_amount for p in payouts if p.age_bracket == "78+"), 0)),
        }
    }


@tool
def compare_plans_for_age(current_age: int) -> Dict[str, Any]:
    """
    Compare all available pension plans for a specific age.
    Use this when user asks "what are my options?" or "compare plans for my age"

    Args:
        current_age: Current age of the person (18-55)

    Returns:
        Dictionary comparing all plans with premiums for this age
    """
    if current_age < 18 or current_age > 55:
        return {"error": "Age must be between 18 and 55"}

    entry_data = _db_session.query(PensionEntryAge).filter(
        PensionEntryAge.entry_age == current_age
    ).first()

    if not entry_data:
        return {"error": f"No data found for age {current_age}"}

    comparison = {
        "current_age": current_age,
        "years_to_retirement": entry_data.years_to_60,
        "options": []
    }

    # Map premiums to pension amounts
    premium_pension_map = [
        (float(entry_data.premium_for_1000), 1000),
        (float(entry_data.premium_for_2500), 2500),
        (float(entry_data.premium_for_5000), 5000),
        (float(entry_data.premium_for_10000), 10000),
    ]

    for premium, pension_60_63 in premium_pension_map:
        total_contribution = premium * 12 * entry_data.years_to_60

        # Find matching plan for full pension breakdown
        matching_plan = _db_session.query(PensionPremiumPlan).filter(
            PensionPremiumPlan.monthly_premium == premium
        ).first()

        pension_breakdown = {}
        if matching_plan:
            payouts = _db_session.query(PensionPayout).filter(
                PensionPayout.plan_id == matching_plan.id
            ).all()
            pension_breakdown = {
                payout.age_bracket: float(payout.pension_amount)
                for payout in payouts
            }

        comparison["options"].append({
            "monthly_premium": premium,
            "total_contribution": round(total_contribution, 2),
            "pension_at_60_63": pension_60_63,
            "full_pension_breakdown": pension_breakdown
        })

    return comparison