from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class PensionPayout(Base):
    __tablename__ = "pension_payouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    age_bracket = Column(String(20), nullable=False)
    pension_amount = Column(Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<PensionPayout {self.age_bracket}: Rs.{self.pension_amount}>"