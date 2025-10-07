from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PensionCalculationRequest(BaseModel):
    current_age: int = Field(..., ge=18, le=55, description="Current age (18-55)")
    desired_pension_amount: float = Field(..., gt=0, description="Desired monthly pension at age 60")


class PensionCalculationResult(BaseModel):
    monthly_contribution: float
    total_months: int
    total_contribution: float
    expected_pension: float
    years_to_retirement: int


class PensionCalculationResponse(BaseModel):
    id: int
    session_id: str
    current_age: int
    desired_pension_amount: float
    monthly_contribution: float
    total_contribution: float
    calculated_at: datetime

    class Config:
        from_attributes = True