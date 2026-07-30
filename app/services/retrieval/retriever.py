"""
Retrieval Service

Handles semantic retrieval of similar solved problems from Qdrant.
"""

from typing import Any

import logfire

from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.flashrank import rerank_documents
from app.services.retrieval.qdrant_service import search


def retrieve_similar_problems(
    problem_statement: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve and rerank the most similar previously solved problems.

    Args:
        problem_statement:
            Current problem statement.

        limit:
            Number of final results to return.

    Returns:
        List of reranked similar problems.
    """

    if not problem_statement.strip():
        return []

    with logfire.span(
        "Retrieve Similar Problems",
        limit=limit,
    ):
        # ---------------------------------------------------------
        # Generate embedding
        # ---------------------------------------------------------
        query_vector = embed_query(problem_statement)

        # ---------------------------------------------------------
        # Retrieve candidates from Qdrant
        # ---------------------------------------------------------
        candidate_results = search(
            query_vector=query_vector,
            limit=max(limit * 4, 20),
        )

        logfire.info(
            f"Retrieved {len(candidate_results)} candidate documents from Qdrant."
        )

        # If nothing found
        if not candidate_results:
            logfire.info("No similar documents found.")
            return []

        # ---------------------------------------------------------
        # FlashRank reranking
        # ---------------------------------------------------------
        with logfire.span("FlashRank Reranking"):

            reranked_results = rerank_documents(
                query=problem_statement,
                retrieved_results=candidate_results,
                top_n=limit,
            )

        logfire.info(
            f"Returning {len(reranked_results)} reranked documents."
        )

        return reranked_results