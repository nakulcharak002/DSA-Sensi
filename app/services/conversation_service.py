from typing import Dict, List


class ConversationService:

    _sessions: Dict[str, dict] = {}

    @classmethod
    def get_session(cls, session_id: str) -> dict:

        if session_id not in cls._sessions:

            cls._sessions[session_id] = {
                "conversation_history": [],
                "hint_level": 0,
                "last_agent": "",
                "problem_statement": "",
                "user_code": "",
                "retrieved_problems": [],
            }

        return cls._sessions[session_id]

    @classmethod
    def append_message(
        cls,
        session_id: str,
        role: str,
        content: str,
    ):

        session = cls.get_session(session_id)

        session["conversation_history"].append(
            {
                "role": role,
                "content": content,
            }
        )

    @classmethod
    def set_hint_level(
        cls,
        session_id: str,
        level: int,
    ):

        session = cls.get_session(session_id)

        session["hint_level"] = level

    @classmethod
    def increase_hint(
        cls,
        session_id: str,
    ):

        session = cls.get_session(session_id)

        session["hint_level"] += 1

    @classmethod
    def get_hint_level(
        cls,
        session_id: str,
    ) -> int:

        return cls.get_session(session_id)["hint_level"]

    @classmethod
    def set_last_agent(
        cls,
        session_id: str,
        agent: str,
    ):

        session = cls.get_session(session_id)

        session["last_agent"] = agent

    @classmethod
    def get_last_agent(
        cls,
        session_id: str,
    ) -> str:

        return cls.get_session(session_id)["last_agent"]

    @classmethod
    def update_problem(
        cls,
        session_id: str,
        problem: str,
    ):

        cls.get_session(session_id)["problem_statement"] = problem

    @classmethod
    def update_code(
        cls,
        session_id: str,
        code: str,
    ):

        cls.get_session(session_id)["user_code"] = code

    @classmethod
    def reset(
        cls,
        session_id: str,
    ):

        if session_id in cls._sessions:
            del cls._sessions[session_id]