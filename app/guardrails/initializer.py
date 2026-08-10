from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails

import logfire

from app.config import settings

_rails: LLMRails | None = None


def initialize_rails() -> None:
    """
    Initialize NeMo Guardrails singleton.
    """

    global _rails

    if _rails is not None:
        return

    guard_llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    config = RailsConfig.from_path("app/guardrails")

    _rails = LLMRails(
        config=config,
        llm=guard_llm,
    )

    logfire.info("🛡️ NeMo Guardrails initialized successfully.")


def get_rails() -> LLMRails:
    if _rails is None:
        raise RuntimeError(
            "Guardrails are not initialized."
        )

    return _rails