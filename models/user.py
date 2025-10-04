from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean

from config.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True),
    name= Column(String(50),index=True, nullable=False),
    birthday = Column(DateTime, index=True,nullable=False),
    email= Column(String(100), unique=True, index=True, nullable=True),
    isMarried= Column(Boolean, index=True, default=False),
