from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.agents.state import AgentState
from app.guardrails.service import guard
from app.services.conversation_service import ConversationService


class ChatService:

    # =====================================================
    # GET HINT
    # =====================================================

    @staticmethod
    def get_hint(
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        hint_level: int,
    ):
        # -------------------------------------------------
        # Verify session ownership
        # -------------------------------------------------

        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        # -------------------------------------------------
        # Build AgentState
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Run LangGraph
        # -------------------------------------------------

        result = graph.invoke(state)

        # -------------------------------------------------
        # Debug
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("GET HINT GRAPH RESULT")
        print("hint_level:", result.get("hint_level"))
        print("last_agent:", result.get("last_agent"))
        print("next_node:", result.get("next_node"))
        print("response:", result.get("response"))
        print("=" * 60 + "\n")

        return result["response"]

    # =====================================================
    # EXECUTE CODE
    # =====================================================

    @staticmethod
    def execute_code(
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        # -------------------------------------------------
        # Verify ownership
        # -------------------------------------------------

        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        # -------------------------------------------------
        # Build AgentState
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Run LangGraph
        # -------------------------------------------------

        result = graph.invoke(state)

        # -------------------------------------------------
        # Debug
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("EXECUTION GRAPH RESULT")
        print("hint_level:", result.get("hint_level"))
        print("last_agent:", result.get("last_agent"))
        print("next_node:", result.get("next_node"))
        print("execution_result:", result.get("execution_result"))
        print("=" * 60 + "\n")

        return result["execution_result"]

    # =====================================================
    # REVIEW CODE
    # =====================================================

    @staticmethod
    def review_code(
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        # -------------------------------------------------
        # Verify ownership
        # -------------------------------------------------

        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        # -------------------------------------------------
        # Build AgentState
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Run LangGraph
        # -------------------------------------------------

        result = graph.invoke(state)

        # -------------------------------------------------
        # Debug
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("REVIEW GRAPH RESULT")
        print("hint_level:", result.get("hint_level"))
        print("last_agent:", result.get("last_agent"))
        print("next_node:", result.get("next_node"))
        print("review:", result.get("review"))
        print("=" * 60 + "\n")

        return result["review"]

    # =====================================================
    # ANALYZE COMPLEXITY
    # =====================================================

    @staticmethod
    def analyze_complexity(
        db: Session,
        user_id: str,
        session_id: str,
        problem_statement: str,
        user_code: str,
    ):

        # -------------------------------------------------
        # Verify ownership
        # -------------------------------------------------

        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        # -------------------------------------------------
        # Build AgentState
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Run LangGraph
        # -------------------------------------------------

        result = graph.invoke(state)

        # -------------------------------------------------
        # Debug
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("COMPLEXITY GRAPH RESULT")
        print("hint_level:", result.get("hint_level"))
        print("last_agent:", result.get("last_agent"))
        print("next_node:", result.get("next_node"))
        print("complexity:", result.get("complexity"))
        print("=" * 60 + "\n")

        return result["complexity"]

    # =====================================================
    # CHAT
    # =====================================================

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
        # 1. Get session and verify ownership
        # -------------------------------------------------

        session = ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        # -------------------------------------------------
        # 2. Update problem statement
        # -------------------------------------------------

        if problem_statement:

            session = ConversationService.update_problem(
                db=db,
                session_id=session_id,
                user_id=user_id,
                problem_statement=problem_statement,
            )

        # -------------------------------------------------
        # 3. Update user code
        # -------------------------------------------------

        if user_code:

            session = ConversationService.update_code(
                db=db,
                session_id=session_id,
                user_id=user_id,
                user_code=user_code,
            )

        # -------------------------------------------------
        # 4. Get conversation history
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
        # 6. Save user's message
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

            "problem_statement": (
                session.problem_statement or ""
            ),

            "user_code": (
                session.user_code or ""
            ),

            "request_type": "",

            # Load persisted hint level
            "hint_level": (
                session.hint_level or 0
            ),

            "next_node": "",

            # Load persisted last agent
            "last_agent": (
                session.last_agent or ""
            ),

            "response": "",

            "review": {},

            "complexity": {},

            "execution_result": {},

            "retrieved_problems": [],
        }

        # -------------------------------------------------
        # DEBUG: State before graph
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("STATE BEFORE GRAPH")
        print("session_id:", session_id)
        print("hint_level:", state["hint_level"])
        print("last_agent:", state["last_agent"])
        print("message:", message)
        print("=" * 60 + "\n")

        # -------------------------------------------------
        # 8. Run LangGraph
        # -------------------------------------------------

        result = graph.invoke(state)

        # -------------------------------------------------
        # DEBUG: Graph result
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("GRAPH RESULT")
        print("hint_level:", result.get("hint_level"))
        print("last_agent:", result.get("last_agent"))
        print("next_node:", result.get("next_node"))
        print("response:", result.get("response"))
        print("review:", result.get("review"))
        print("complexity:", result.get("complexity"))
        print(
            "execution_result:",
            result.get("execution_result"),
        )
        print("=" * 60 + "\n")

        # -------------------------------------------------
        # 9. Persist updated agent state
        # -------------------------------------------------

        session.hint_level = result.get(
            "hint_level",
            session.hint_level or 0,
        )

        session.last_agent = result.get(
            "last_agent",
            session.last_agent or "",
        )

        print("\n" + "=" * 60)
        print("PERSISTING SESSION")
        print("hint_level:", session.hint_level)
        print("last_agent:", session.last_agent)
        print("=" * 60 + "\n")

        db.commit()

        # -------------------------------------------------
        # 10. Handle normal response / hint
        # -------------------------------------------------

        if result.get("response"):

            response = str(
                result["response"]
            )

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["response"]

        # -------------------------------------------------
        # 11. Handle code review
        # -------------------------------------------------

        if result.get("review"):

            response = str(
                result["review"]
            )

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["review"]

        # -------------------------------------------------
        # 12. Handle complexity analysis
        # -------------------------------------------------

        if result.get("complexity"):

            response = str(
                result["complexity"]
            )

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["complexity"]

        # -------------------------------------------------
        # 13. Handle code execution
        # -------------------------------------------------

        if result.get("execution_result"):

            response = str(
                result["execution_result"]
            )

            ConversationService.append_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )

            return result["execution_result"]

        # -------------------------------------------------
        # 14. Nothing generated
        # -------------------------------------------------

        return "No response generated."