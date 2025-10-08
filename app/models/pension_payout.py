# app/models/pension_payout.py
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class PensionPayout(Base):
    """Pension amounts for different age brackets and premium plans"""
    __tablename__ = "pension_payouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("pension_premium_plans.id"), nullable=False)

    # Age bracket for receiving pension
    age_bracket = Column(String(20), nullable=False)  # "60-63", "64-70", "71-77", "78+"

    # Pension amount for this bracket
    pension_amount = Column(Numeric(10, 2), nullable=False)

    # Relationships
    plan = relationship("PensionPremiumPlan", backref="payouts")

    def __repr__(self):
        return f"<PensionPayout {self.age_bracket}: Rs.{self.pension_amount}>"