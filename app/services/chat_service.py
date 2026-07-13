from app.agents.graph import graph
from app.agents.state import AgentState


class ChatService:

    @staticmethod
    def get_hint(
        session_id: str,
        problem_statement: str,
        hint_level: int,
    ):

        state: AgentState = {
            "session_id": session_id,

            "messages": [
                {
                    "role": "user",
                    "content": problem_statement,
                }
            ],

            "problem_statement": problem_statement,

            "user_code": "",

            "request_type": "",

            "hint_level": hint_level,

            "next_node": "",

            "response": "",

            "review": {},

            "complexity": {},

            "execution_result": {},
        }

        result = graph.invoke(state)

        return result["response"]

    @staticmethod
    def execute_code(
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        state: AgentState = {
            "session_id": session_id,

            "messages": [
                {
                    "role": "user",
                    "content": "Please execute my C++ code.",
                }
            ],

            "problem_statement": problem_statement,

            "user_code": user_code,

            "request_type": "execution",

            "hint_level": 0,

            "next_node": "",

            "response": "",

            "review": {},

            "complexity": {},

            "execution_result": {},
        }

        result = graph.invoke(state)

        return result["execution_result"]