"""
Seed Qdrant with sample DSA problems.

Run:
python -m app.scripts.seed_qdrant
"""

from uuid import uuid4

from app.services.retrieval.embeddings import embed_texts
from app.services.retrieval.qdrant_service import (
    create_collection,
    delete_collection,
    upsert,
)

SAMPLE_PROBLEMS = [
    {
        "title": "Two Sum",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "difficulty": "Easy",
        "topics": ["Array", "HashMap"],
        "solution": "Use a hash map to store visited values.",
    },
    {
        "title": "Binary Search",
        "problem": "Given a sorted array and a target, return the index of the target.",
        "difficulty": "Easy",
        "topics": ["Binary Search"],
        "solution": "Maintain low and high pointers.",
    },
    {
        "title": "Merge Intervals",
        "problem": "Merge all overlapping intervals.",
        "difficulty": "Medium",
        "topics": ["Sorting", "Intervals"],
        "solution": "Sort by start time and merge.",
    },
    {
        "title": "Longest Increasing Subsequence",
        "problem": "Return the length of the longest increasing subsequence.",
        "difficulty": "Medium",
        "topics": ["DP", "Binary Search"],
        "solution": "DP or patience sorting.",
    },
    {
        "title": "Number of Islands",
        "problem": "Count the number of islands in a grid.",
        "difficulty": "Medium",
        "topics": ["DFS", "BFS", "Graph"],
        "solution": "Run DFS/BFS from every unvisited land cell.",
    },
]


def main():
    print("Deleting old collection...")
    delete_collection()

    print("Creating collection...")
    create_collection()

    print("Generating embeddings...")
    vectors = embed_texts(
        [problem["problem"] for problem in SAMPLE_PROBLEMS]
    )

    print("Embeddings generated.")

    payloads = [
        {
            "title": p["title"],
            "problem": p["problem"],
            "solution": p["solution"],
            "difficulty": p["difficulty"],
            "topics": p["topics"],
        }
        for p in SAMPLE_PROBLEMS
    ]

    ids = [str(uuid4()) for _ in SAMPLE_PROBLEMS]

    print("Generated IDs:")
    for uid in ids:
        print(uid)

    print("Uploading...")

    upsert(
        ids=ids,
        vectors=vectors,
        payloads=payloads,
    )

    print("✅ Successfully seeded Qdrant!")


if __name__ == "__main__":
    main()