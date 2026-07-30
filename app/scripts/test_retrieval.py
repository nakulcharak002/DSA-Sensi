from app.services.retrieval.retriever import retrieve_similar_problems

results = retrieve_similar_problems(
    problem_statement="""
Given an array of integers and a target,
return indices of two numbers whose sum equals the target.
""",
    limit=5,
)

print("\nRetrieved Problems:\n")

for i, result in enumerate(results, 1):
    payload = result["payload"]

    print(f"{i}. {payload['title']}")
    print("Score:", result["score"])
    print("Topics:", payload["topics"])
    print()