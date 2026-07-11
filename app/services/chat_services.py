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

            "hint_level": hint_level,

            "next_node": "",

            "response": "",
        }

        result = graph.invoke(state)

        return result["response"]