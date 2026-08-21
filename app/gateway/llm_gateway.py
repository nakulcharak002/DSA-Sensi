from langchain_groq import ChatGroq
from app.config import settings


def get_langchain_llm(feature: str = "default"):
    settings.require("GROQ_API_KEY")

    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )