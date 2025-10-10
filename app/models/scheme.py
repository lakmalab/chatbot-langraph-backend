from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, Boolean
from app.db.connection import Base
from app.enums.scheme import SchemeType


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_type = Column(SQLEnum(SchemeType, name="scheme_type"), nullable=False)
    scheme_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Scheme {self.scheme_name}>"