from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.enums import AiModel

def get_llm(temperature: float = 0, provider:AiModel=AiModel.OPENAI):
    if provider == AiModel.OPENAI:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        return ChatOpenAI(
            model=settings.OPENAI_AI_MODEL,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")