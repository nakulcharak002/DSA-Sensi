from app.agents.graph import graph

state = {
    "session_id": "123",

    "messages": [
        {
            "role": "user",
            "content": "Give me a hint for Two Sum"
        }
    ],

    "problem_statement": "Two Sum",

    "user_code": "",

    "hint_level": 0,

    "next_node": "",

    "response": "",
}

result = graph.invoke(state)

print(result)