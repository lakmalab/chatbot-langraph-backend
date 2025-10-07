from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.db.connection import get_db
from app.schemas.pension import PensionCalculationRequest, PensionCalculationResult
from app.utils.pension_calculator import PensionCalculator

router = APIRouter(prefix="/api/v2/pension", tags=["Pension"])


@router.post("/calculate", response_model=PensionCalculationResult)
async def calculate_pension(
        request: PensionCalculationRequest,
        db: DBSession = Depends(get_db)
):

    calculator = PensionCalculator()

    try:
        result = calculator.calculate_monthly_contribution(
            current_age=request.current_age,
            desired_monthly_pension=request.desired_pension_amount
        )

        return PensionCalculationResult(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/calculations/{session_id}")
async def get_pension_calculations(
        session_id: str,
        db: DBSession = Depends(get_db)
):

    from app.models.pension_calculation import PensionCalculation

    calculations = db.query(PensionCalculation).filter(
        PensionCalculation.session_id == session_id
    ).order_by(PensionCalculation.calculated_at.desc()).all()

    return {
        "session_id": session_id,
        "calculations": [
            {
                "id": calc.id,
                "current_age": calc.current_age,
                "desired_pension_amount": float(calc.desired_pension_amount),
                "monthly_contribution": float(calc.monthly_contribution),
                "total_contribution": float(calc.total_contribution),
                "calculated_at": calc.calculated_at
            }
            for calc in calculations
        ]
    }