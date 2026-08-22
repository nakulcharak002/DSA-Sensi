from typing import Any

from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.agents.state import AgentState
from app.guardrails.service import guard
from app.services.conversation_service import ConversationService


class ChatService:

    @staticmethod
    def get_hint(
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        hint_level: int,
    ):

        # Verify that this session belongs to this user
        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

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
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        # Verify ownership
        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

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
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        # Verify ownership
        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

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
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        # Verify ownership
        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        state: AgentState = {
            "session_id": session_id,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Analyze the time and space complexity "
                        "of my C++ code."
                    ),
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
        db: Session,
        user_id: str,
        session_id: str,
        message: str,
        problem_statement: str = "",
        user_code: str = "",
    ):

        # -------------------------------------------------
        # 1. Get the session and verify ownership
        # -------------------------------------------------

        session = ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        # -------------------------------------------------
        # 2. Update problem statement if provided
        # -------------------------------------------------

        if problem_statement:

            session = ConversationService.update_problem(
                db=db,
                session_id=session_id,
                user_id=user_id,
                problem_statement=problem_statement,
            )

        # -------------------------------------------------
        # 3. Update user code if provided
        # -------------------------------------------------

        if user_code:

            session = ConversationService.update_code(
                db=db,
                session_id=session_id,
                user_id=user_id,
                user_code=user_code,
            )

        # -------------------------------------------------
        # 4. Get previous conversation history from DB
        # -------------------------------------------------

        messages = ConversationService.get_messages(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        # -------------------------------------------------
        # 5. NeMo Guardrails
        # -------------------------------------------------

        blocked, guard_response = guard(message)

        if blocked:

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=guard_response,
            )

            return guard_response

        # -------------------------------------------------
        # 6. Save user's message to PostgreSQL
        # -------------------------------------------------

        ConversationService.append_message(
            db=db,
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=message,
        )

        # -------------------------------------------------
        # 7. Build AgentState
        # -------------------------------------------------

        state: AgentState = {
            "session_id": session_id,

            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],

            "conversation_history": conversation_history,

            "problem_statement": session.problem_statement or "",

            "user_code": session.user_code or "",

            "request_type": "",

            "hint_level": 0,

            "next_node": "",

            "last_agent": "",

            "response": "",

            "review": {},

            "complexity": {},

            "execution_result": {},

            "retrieved_problems": [],
        }

        # -------------------------------------------------
        # 8. Run LangGraph
        # -------------------------------------------------

        result = graph.invoke(state)

        # -------------------------------------------------
        # 9. Handle normal response / hint
        # -------------------------------------------------

        if result.get("response"):

            response = str(result["response"])

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["response"]

        # -------------------------------------------------
        # 10. Handle code review
        # -------------------------------------------------

        if result.get("review"):

            response = str(result["review"])

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["review"]

        # -------------------------------------------------
        # 11. Handle complexity analysis
        # -------------------------------------------------

        if result.get("complexity"):

            response = str(result["complexity"])

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["complexity"]

        # -------------------------------------------------
        # 12. Handle code execution
        # -------------------------------------------------

        if result.get("execution_result"):

            response = str(result["execution_result"])

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["execution_result"]

        # -------------------------------------------------
        # 13. Nothing generated
        # -------------------------------------------------

        return "No response generated."