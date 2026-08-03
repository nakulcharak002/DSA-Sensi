"""
Memory Service

Stores solved DSA problems into Qdrant so they can be
retrieved later for personalized hints.
"""

from datetime import UTC, datetime
from uuid import uuid4

import logfire

from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.metadata_extractor import extract_metadata
from app.services.retrieval.qdrant_service import upsert


def save_solved_problem(
    problem: str,
    solution: str,
    language: str,
    hint_level: int,
    attempts: int,
    review_score: int | None = None,
    time_complexity: str | None = None,
    space_complexity: str | None = None,
    status: str = "Solved",
) -> str:
    """
    Save a solved DSA problem into Qdrant.

    Metadata (title, difficulty, topics) is automatically
    extracted using the Metadata Extractor.
    """

    logfire.info("Extracting problem metadata...")

    metadata = extract_metadata(problem)

    logfire.info(
        f"Metadata extracted: {metadata.title}"
    )

    problem_id = str(uuid4())

    embedding = embed_query(problem)

    payload = {
        "title": metadata.title,
        "problem": problem,
        "solution": solution,
        "difficulty": metadata.difficulty,
        "topics": metadata.topics,
        "language": language,
        "hint_level": hint_level,
        "attempts": attempts,
        "review_score": review_score,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "status": status,
        "created_at": datetime.now(UTC).isoformat(),
    }

    upsert(
        ids=[problem_id],
        vectors=[embedding],
        payloads=[payload],
    )

    logfire.info(
        f"Saved '{metadata.title}' into Qdrant."
    )

    return problem_id