import logfire

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from app.config import settings
from app.services.retrieval.embeddings import get_embedding_dim

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------

_client = None
_collection = None
_student_collection = None

# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

def _init():
    """
    Initialize the Qdrant client once.
    """

    global _client
    global _collection
    global _student_collection

    if _client is not None:
        return

    settings.require(
        "QDRANT_CLUSTER_ENDPOINT",
        "QDRANT_API_KEY",
    )

    _client = QdrantClient(
        url=settings.QDRANT_CLUSTER_ENDPOINT,
        api_key=settings.QDRANT_API_KEY,
    )

    _collection = getattr(
        settings,
        "QDRANT_COLLECTION",
        "dsa_problems",
    )

    # Separate collection for student-solved solutions.
    # Kept apart from `_collection` (the curated reference problems)
    # so hint retrieval never accidentally surfaces raw student code
    # as "similar context" -> prevents solution leakage.
    _student_collection = getattr(
        settings,
        "QDRANT_STUDENT_COLLECTION",
        "student_solutions",
    )

    logfire.info(
        f"Connected to Qdrant collection '{_collection}'."
    )

# -----------------------------------------------------------------------------
# Collection (generic helpers, operate on a given collection name)
# -----------------------------------------------------------------------------

def _collection_exists(collection_name: str) -> bool:

    _init()

    collections = _client.get_collections()

    return any(
        c.name == collection_name
        for c in collections.collections
    )


def _create_collection(collection_name: str):

    _init()

    if _collection_exists(collection_name):
        logfire.info(
            f"Collection '{collection_name}' already exists."
        )
        return

    _client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=get_embedding_dim(),
            distance=Distance.COSINE,
        ),
    )

    logfire.info(
        f"Collection '{collection_name}' created successfully."
    )


def _upsert_to(
    collection_name: str,
    ids: list[str],
    vectors: list[list[float]],
    payloads: list[dict],
):

    _init()

    if not _collection_exists(collection_name):
        _create_collection(collection_name)

    if not (len(ids) == len(vectors) == len(payloads)):
        raise ValueError(
            "ids, vectors and payloads must have the same length."
        )

    points = [
        PointStruct(
            id=id_,
            vector=vector,
            payload=payload,
        )
        for id_, vector, payload in zip(ids, vectors, payloads)
    ]

    with logfire.span(
        "Qdrant Upsert",
        collection=collection_name,
        count=len(points),
    ):
        _client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points,
        )

    logfire.info(
        f"Successfully upserted {len(points)} vectors into '{collection_name}'."
    )

# -----------------------------------------------------------------------------
# Public API - reference problems collection (unchanged behavior)
# -----------------------------------------------------------------------------

def collection_exists() -> bool:
    """
    Returns True if the reference-problems collection already exists.
    """

    _init()

    return _collection_exists(_collection)


def create_collection():
    """
    Creates the reference-problems collection if it does not already exist.
    """

    _init()

    _create_collection(_collection)


def delete_collection():
    """
    Delete the reference-problems collection.
    """

    _init()

    if not _collection_exists(_collection):
        return

    _client.delete_collection(
        collection_name=_collection,
    )

    logfire.info(
        f"Collection '{_collection}' deleted."
    )


def upsert(
    ids: list[str],
    vectors: list[list[float]],
    payloads: list[dict],
):
    """
    Insert or update vectors in the reference-problems collection.
    """

    _init()

    _upsert_to(_collection, ids, vectors, payloads)


def search(
    query_vector: list[float],
    limit: int = 5,
):
    """
    Search similar vectors from the reference-problems collection ONLY.
    Student-solved solutions live in a separate collection and are
    never returned here, so hint retrieval can't leak solution code.
    """

    _init()

    with logfire.span(
        "Qdrant Search",
        collection=_collection,
        limit=limit,
    ):
        response = _client.query_points(
            collection_name=_collection,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

    results = []

    for point in response.points:
        results.append(
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload,
            }
        )

    logfire.info(
        f"Retrieved {len(results)} similar documents."
    )

    return results

# -----------------------------------------------------------------------------
# Public API - student-solved-solutions collection
# -----------------------------------------------------------------------------

def search_student_solutions(
    query_vector: list[float],
    limit: int = 1,
):
    """
    Search the student_solutions collection ONLY.
    Used to detect "has this student solved this problem before",
    never to pull solution_code into hint context.
    """

    _init()

    if not _collection_exists(_student_collection):
        # No student has solved anything yet -> nothing to find.
        return []

    with logfire.span(
        "Qdrant Search",
        collection=_student_collection,
        limit=limit,
    ):
        response = _client.query_points(
            collection_name=_student_collection,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

    results = []

    for point in response.points:
        results.append(
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload,
            }
        )

    return results


def store_solved_problem(
    problem_statement: str,
    solution_code: str,
    execution_result: dict,
):
    """
    Store a successfully solved problem in its own Qdrant collection
    (kept separate from the reference-problems collection used by
    hint retrieval, to avoid ever surfacing raw student solution
    code as retrieval context).
    """

    from uuid import uuid4
    from app.services.retrieval.embeddings import embed_query

    if not problem_statement.strip():
        return

    _init()

    vector = embed_query(problem_statement)

    point_id = str(uuid4())

    payload = {
        "problem": problem_statement,
        "solution_code": solution_code,
        "execution_result": execution_result,
        "type": "student_solved_problem",
    }

    _upsert_to(
        _student_collection,
        ids=[point_id],
        vectors=[vector],
        payloads=[payload],
    )

    logfire.info(
        f"Stored solved problem in Qdrant: {point_id}"
    )