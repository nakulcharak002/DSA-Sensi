import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    GROQ_FALLBACK_API_KEY: str = os.environ.get("GROQ_FALLBACK_API_KEY", "")
    PORTKEY_API_KEY: str = os.environ.get("PORTKEY_API_KEY", "")
    QDRANT_API_KEY: str = os.environ.get("QDRANT_API_KEY", "")
    QDRANT_CLUSTER_ENDPOINT: str = os.environ.get("QDRANT_CLUSTER_ENDPOINT", "")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    LOGFIRE_TOKEN: str = os.environ.get("LOGFIRE_TOKEN", "")
    LANGSMITH_TRACING: bool = os.environ.get("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_ENDPOINT: str = os.environ.get("LANGSMITH_ENDPOINT", "")
    LANGSMITH_API_KEY: str = os.environ.get("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.environ.get("LANGSMITH_PROJECT", "dsa-sensei")
    JUDGE_GROQ: str = os.environ.get("JUDGE_GROQ", "")
    BACKEND_URL: str = os.environ.get("BACKEND_URL", "http://localhost:8000")
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "")

    def require(self, *names: str) -> None:
        missing = [n for n in names if not getattr(self, n, None)]
        if missing:
            raise RuntimeError(
                f"Missing required environment variable(s): {', '.join(missing)}. "
                f"Set them in your .env file."
            )


settings = Settings()
