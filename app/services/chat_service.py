from app.agents.graph import graph
from app.agents.state import AgentState
from typing import Any
from app.services.conversation_service import ConversationService


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
            "conversation_history": [],
            "problem_statement": problem_statement,
            "user_code": "",
            "request_type": "",
            "hint_level": hint_level,
            "next_node": "",
            "last_agent": "",
            "response": "",
            "review": {},
            "complexity": {},
            "execution_result": {},
            "retrieved_problems": [],
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
            "conversation_history": [],
            "problem_statement": problem_statement,
            "user_code": user_code,
            "request_type": "execution",
            "hint_level": 0,
            "next_node": "",
            "last_agent": "",
            "response": "",
            "review": {},
            "complexity": {},
            "execution_result": {},
            "retrieved_problems": [],
        }

        result = graph.invoke(state)

        return result["execution_result"]

    @staticmethod
    def review_code(
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        state: AgentState = {
            "session_id": session_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Please review my C++ code.",
                }
            ],
            "conversation_history": [],
            "problem_statement": problem_statement,
            "user_code": user_code,
            "request_type": "review",
            "hint_level": 0,
            "next_node": "",
            "last_agent": "",
            "response": "",
            "review": {},
            "complexity": {},
            "execution_result": {},
            "retrieved_problems": [],
        }

        result = graph.invoke(state)

        return result["review"]

    @staticmethod
    def analyze_complexity(
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        state: AgentState = {
            "session_id": session_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Analyze the time and space complexity of my C++ code.",
                }
            ],
            "conversation_history": [],
            "problem_statement": problem_statement,
            "user_code": user_code,
            "request_type": "complexity",
            "hint_level": 0,
            "next_node": "",
            "last_agent": "",
            "response": "",
            "review": {},
            "complexity": {},
            "execution_result": {},
            "retrieved_problems": [],
        }

        result = graph.invoke(state)

        return result["complexity"]

    @staticmethod
    def chat(
        session_id: str,
        message: str,
        problem_statement: str = "",
        user_code: str = "",
    ):

        session = ConversationService.get_session(session_id)

        if problem_statement:
            ConversationService.update_problem(
                session_id,
                problem_statement,
            )

        if user_code:
            ConversationService.update_code(
                session_id,
                user_code,
            )

        ConversationService.append_message(
            session_id,
            "user",
            message,
        )

        state: AgentState = {
            "session_id": session_id,
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "conversation_history": session["conversation_history"],
            "problem_statement": session["problem_statement"],
            "user_code": session["user_code"],
            "request_type": "",
            "hint_level": session["hint_level"],
            "next_node": "",
            "last_agent": session["last_agent"],
            "response": "",
            "review": {},
            "complexity": {},
            "execution_result": {},
            "retrieved_problems": session["retrieved_problems"],
        }

        result = graph.invoke(state)

        if "retrieved_problems" in result:

            session["retrieved_problems"] = result["retrieved_problems"]

        if result.get("response"):

            ConversationService.append_message(
                session_id,
                "assistant",
                str(result["response"]),
            )

            ConversationService.set_last_agent(
                session_id,
                "hint",
            )

            return result["response"]

        if result.get("review"):

            ConversationService.append_message(
                session_id,
                "assistant",
                str(result["review"]),
            )

            ConversationService.set_last_agent(
                session_id,
                "review",
            )

            return result["review"]

        if result.get("complexity"):

            ConversationService.append_message(
                session_id,
                "assistant",
                str(result["complexity"]),
            )

            ConversationService.set_last_agent(
                session_id,
                "complexity",
            )

            return result["complexity"]

        if result.get("execution_result"):

            ConversationService.append_message(
                session_id,
                "assistant",
                str(result["execution_result"]),
            )

            ConversationService.set_last_agent(
                session_id,
                "execution",
            )

            return result["execution_result"]

        return "No response generated."