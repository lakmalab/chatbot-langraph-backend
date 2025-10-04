from datetime import datetime

from pydantic import BaseModel

from config.db import Base


class User(Base):


    id: int
    name: str
    birthday: datetime
    email: str
    isMarried: bool
