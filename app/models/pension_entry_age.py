# app/models/pension_entry_age.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class PensionEntryAge(Base):
    """Premium amounts based on entry age (from the first image table)"""
    __tablename__ = "pension_entry_ages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entry_age = Column(Integer, nullable=False)  # 18, 19, 20, ... 55

    # Premium amounts for different pension targets
    premium_for_1000 = Column(Numeric(10, 2), nullable=False)  # Column for 1000 pension
    premium_for_2500 = Column(Numeric(10, 2), nullable=False)  # Column for 2500 pension
    premium_for_5000 = Column(Numeric(10, 2), nullable=False)  # Column for 5000 pension
    premium_for_10000 = Column(Numeric(10, 2), nullable=False)  # Column for 10000 pension

    years_to_60 = Column(Integer, nullable=False)  # Years remaining until age 60

    def __repr__(self):
        return f"<PensionEntryAge {self.entry_age} years>"