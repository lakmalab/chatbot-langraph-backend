from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class PensionPremium(Base):
    __tablename__ = "pension_entry_ages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entry_age = Column(Integer, nullable=False)
    monthly_premium = Column(Numeric(10, 2), nullable=False)
    num_of_monthly_installments = Column(Numeric(10, 2), nullable=False)
    semi_annual_premium = Column(Numeric(10, 2), nullable=False)
    num_of_semi_annual_installments = Column(Numeric(10, 2), nullable=False)
    lump_sum_payment = Column(Numeric(10, 2), nullable=False)

    def __repr__(self):
        return (
            f"<PensionEntryAge(id={self.id}, "
            f"entry_age={self.entry_age}, "
            f"monthly_premium={self.monthly_premium}, "
            f"num_of_monthly_installments={self.num_of_monthly_installments}, "
            f"semi_annual_premium={self.semi_annual_premium}, "
            f"num_of_semi_annual_installments={self.num_of_semi_annual_installments}, "
            f"lump_sum_payment={self.lump_sum_payment})>"
        )