import time

import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sentence_transformers import SentenceTransformer

from app.config import settings

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

BATCH_SIZE = 50

GEMINI_MODEL = "models/gemini-embedding-2-preview"
GEMINI_DIM = 3072

FALLBACK_MODEL = "BAAI/bge-small-en-v1.5"
FALLBACK_DIM = 384

_active_model = None
_provider = None


# -----------------------------------------------------------------------------
# Provider Initialization
# -----------------------------------------------------------------------------

def _probe_gemini():
    """
    Try loading Gemini embeddings.
    Returns the model if successful, otherwise None.
    """

    if not settings.GEMINI_API_KEY:
        logfire.warning("Gemini API key not found.")
        return None

    try:
        model = GoogleGenerativeAIEmbeddings(
            model=GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )

        # Test with a small embedding request
        model.embed_query("Hello")

        logfire.info("Gemini Embedding Model Loaded Successfully.")

        return model

    except Exception as e:
        logfire.warning(f"Gemini unavailable: {e}")

        return None


def _load_fallback():
    """
    Load the local sentence-transformer model.
    """

    logfire.info(f"Loading fallback model: {FALLBACK_MODEL}")

    return SentenceTransformer(FALLBACK_MODEL)


def _init():
    """
    Initialize the embedding provider once.
    """

    global _active_model
    global _provider

    if _active_model is not None:
        return

    gemini = _probe_gemini()

    if gemini is not None:
        _active_model = gemini
        _provider = "gemini"

    else:
        _active_model = _load_fallback()
        _provider = "sentence-transformer"

    logfire.info(f"Embedding Provider: {_provider}")


# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------

def get_provider() -> str:
    _init()
    return _provider


def get_embedding_dim() -> int:
    _init()

    if _provider == "gemini":
        return GEMINI_DIM

    return FALLBACK_DIM


def is_gemini_active() -> bool:
    _init()

    return _provider == "gemini"


# -----------------------------------------------------------------------------
# Internal Batch Embedding
# -----------------------------------------------------------------------------

def _embed_batch(batch: list[str]) -> list[list[float]]:
    """
    Embed a batch of documents.
    """

    if _provider == "gemini":

        for attempt in range(4):

            try:
                return _active_model.embed_documents(batch)

            except Exception as e:

                message = str(e).lower()

                is_retryable = any(
                    x in message
                    for x in [
                        "429",
                        "quota",
                        "rate",
                        "resource_exhausted",
                    ]
                )

                if is_retryable and attempt < 3:

                    wait = 2 ** attempt

                    logfire.warning(
                        f"Rate limit hit. Retrying in {wait} seconds..."
                    )

                    time.sleep(wait)

                else:

                    logfire.error(f"Embedding failed: {e}")

                    raise

        raise RuntimeError("Embedding failed after retries.")

    embeddings = _active_model.encode(
        batch,
        show_progress_bar=False,
    )

    return embeddings.tolist()


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def embed_query(query: str) -> list[float]:
    """
    Embed a single query.
    """

    _init()

    if _provider == "gemini":
        return _active_model.embed_query(query)

    return _active_model.encode([query])[0].tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple documents in batches.
    """

    _init()

    vectors = []

    for start in range(0, len(texts), BATCH_SIZE):

        batch = texts[start:start + BATCH_SIZE]

        with logfire.span(
            "Embedding Batch",
            provider=_provider,
            batch_size=len(batch),
        ):
            vectors.extend(_embed_batch(batch))

    return vectors






