from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "AAIB Chatbot Assistant"
    APP_VERSION: str = "1.0.0"

    DEBUG:bool = False
    ALLOWED_ORIGINS: str = ""
    API_PREFIX:str = "/api"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str

    SESSION_EXPIRE_HOURS: int
    OPENAI_API_KEY:str
    API_BASE_URL: str = "http://localhost:8000"

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> list[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()