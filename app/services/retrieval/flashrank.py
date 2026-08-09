"""
FlashRank Reranker

Uses a Cross-Encoder model to rerank Qdrant retrieval results.
"""

import time
from typing import Any

import logfire
from flashrank import Ranker, RerankRequest
_ranker: Ranker | None = None


def _get_ranker() -> Ranker:
    """
    Lazily initialize FlashRank.
    """

    global _ranker

    if _ranker is None:
        logfire.info("Initializing FlashRank...")

        try:
            _ranker = Ranker(
                cache_dir="/tmp/flashrank",
            )
        except Exception:
            _ranker = Ranker()

    return _ranker


# -----------------------------------------------------------------------------
# Reranking
# -----------------------------------------------------------------------------

def rerank_documents(
    query: str,
    retrieved_results: list[dict[str, Any]],
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """
    Rerank Qdrant retrieval results using FlashRank.
    """

    if not retrieved_results:
        return []

    start = time.perf_counter()

    try:
        ranker = _get_ranker()

        passages = []

        for idx, result in enumerate(retrieved_results):

            payload = result.get("payload", {})

            text = "\n".join(
                [
                    payload.get("title", ""),
                    payload.get("problem", ""),
                    payload.get("solution", ""),
                ]
            )

            passages.append(
                {
                    "id": idx,
                    "text": text,
                }
            )

        request = RerankRequest(
            query=query,
            passages=passages,
        )

        ranked = ranker.rerank(request)

        reranked = []

        for item in ranked[:top_n]:

            original = retrieved_results[item["id"]].copy()
            original["rerank_score"] = item["score"]

            reranked.append(original)

        elapsed = time.perf_counter() - start

        logfire.info(
            f"FlashRank reranked {len(reranked)} documents in {elapsed:.3f}s."
        )

        return reranked

    except Exception as exc:

        logfire.exception(
            f"FlashRank reranking failed: {exc}"
        )

        return retrieved_results[:top_n]