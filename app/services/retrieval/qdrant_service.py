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


# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

def _init():
    """
    Initialize the Qdrant client once.
    """

    global _client
    global _collection

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

    logfire.info(
        f"Connected to Qdrant collection '{_collection}'."
    )


# -----------------------------------------------------------------------------
# Collection
# -----------------------------------------------------------------------------

def collection_exists() -> bool:
    """
    Returns True if the collection already exists.
    """

    _init()

    collections = _client.get_collections()

    return any(
        c.name == _collection
        for c in collections.collections
    )


def create_collection():
    """
    Creates the collection if it does not already exist.
    """

    _init()

    if collection_exists():
        logfire.info(
            f"Collection '{_collection}' already exists."
        )
        return

    _client.create_collection(
        collection_name=_collection,
        vectors_config=VectorParams(
            size=get_embedding_dim(),
            distance=Distance.COSINE,
        ),
    )

    logfire.info(
        f"Collection '{_collection}' created successfully."
    )


def delete_collection():
    """
    Delete the collection.
    """

    _init()

    if not collection_exists():
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
    Insert or update vectors in the collection.
    """

    _init()

    if not collection_exists():
        create_collection()

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
        collection=_collection,
        count=len(points),
    ):
        _client.upsert(
            collection_name=_collection,
            wait=True,
            points=points,
        )

    logfire.info(
        f"Successfully upserted {len(points)} vectors."
    )
def search(
    query_vector: list[float],
    limit: int = 5,
):
    """
    Search similar vectors from Qdrant.
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