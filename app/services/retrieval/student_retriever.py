from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.qdrant_service import search_student_solutions

SIMILARITY_THRESHOLD = 0.90


def has_solved_before(problem_statement: str, user_id: str) -> bool:
    if not problem_statement.strip():
        return False

    vector = embed_query(problem_statement)

    results = search_student_solutions(
        query_vector=vector,
        user_id=user_id,
        limit=1,
    )

    if not results:
        return False

    top_score = results[0].get("score", 0)

    return top_score >= SIMILARITY_THRESHOLD
