from app.agents.nodes.hint_node import hint_node

state = {
    "problem_statement": """
Given an array of integers nums and an integer target,
return the indices of two numbers such that they add up to the target.
""",
    "hint_level": 0,
    "retrieved_problems": [],
    "response": "",
}

result = hint_node(state)

print("\n========== HINT ==========\n")
print(result["response"])

print("\n========== RETRIEVED ==========\n")

for idx, problem in enumerate(result["retrieved_problems"], start=1):
    payload = problem["payload"]

    print(f"{idx}. {payload['title']}")
    print(f"Topics: {payload['topics']}")
    print(f"Score: {problem.get('rerank_score', problem['score'])}")
    print()