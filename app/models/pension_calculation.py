from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.connection import Base


class PensionCalculation(Base):
    __tablename__ = "pension_calculations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    current_age = Column(Integer, nullable=False)
    desired_pension_amount = Column(Numeric(10, 2), nullable=False)
    monthly_contribution = Column(Numeric(10, 2), nullable=False)
    total_contribution = Column(Numeric(12, 2), nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PensionCalculation {self.id}>"