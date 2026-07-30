"""
Memory Service

Stores solved DSA problems into Qdrant so they can be retrieved
for future personalized hints.
"""

from uuid import uuid4

import logfire

from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.qdrant_service import upsert


def save_problem(
    title: str,
    problem: str,
    solution: str,
    difficulty: str,
    topics: list[str],
    hint_level: int,
    attempts: int,
) -> str:
    """
    Save a solved problem into Qdrant.

    Args:
        title:
            Problem title.

        problem:
            Problem statement.

        solution:
            User's final solution or solution summary.

        difficulty:
            Easy / Medium / Hard.

        topics:
            List of DSA topics.

        hint_level:
            Highest hint tier used.

        attempts:
            Number of submissions.

    Returns:
        Generated problem ID.
    """

    problem_id = str(uuid4())

    embedding = embed_query(problem)

    payload = {
        "title": title,
        "problem": problem,
        "solution": solution,
        "difficulty": difficulty,
        "topics": topics,
        "hint_level": hint_level,
        "attempts": attempts,
    }

    upsert(
        ids=[problem_id],
        vectors=[embedding],
        payloads=[payload],
    )

    logfire.info(
        "Saved solved problem '{}' into memory.",
        title,
    )

    return problem_id