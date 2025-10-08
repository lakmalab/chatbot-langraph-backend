from sqlalchemy import Column, Integer, Numeric, String, Boolean
from app.db.connection import Base


class PensionPremiumPlan(Base):
    """Fixed premium plans (e.g., Rs. 27, 270, 2700 per month)"""
    __tablename__ = "pension_premium_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_name = Column(String(100), nullable=False)  # e.g., "Basic Plan", "Standard Plan", "Premium Plan"
    monthly_premium = Column(Numeric(10, 2), nullable=False)  # Rs. 27, 270, 2700
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<PensionPremiumPlan {self.plan_name} - Rs.{self.monthly_premium}>"