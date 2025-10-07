import enum

class RoleType(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    BOT = "bot"
