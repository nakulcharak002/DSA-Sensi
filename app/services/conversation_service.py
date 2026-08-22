from sqlalchemy.orm import Session

from app.repositories.conversation_repository import ConversationRepository


class ConversationService:

    @staticmethod
    def create_session(
        db: Session,
        user_id: str,
        problem_statement: str = "",
    ):
        return ConversationRepository.create_session(
            db=db,
            user_id=user_id,
            problem_statement=problem_statement,
        )

    @staticmethod
    def get_session(
        db: Session,
        session_id: str,
        user_id: str,
    ):
        conversation = ConversationRepository.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        if not conversation:
            raise ValueError("Session not found")

        return conversation

    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: str,
    ):
        return ConversationRepository.get_user_sessions(
            db=db,
            user_id=user_id,
        )

    @staticmethod
    def update_problem(
        db: Session,
        session_id: str,
        user_id: str,
        problem_statement: str,
    ):
        conversation = ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        return ConversationRepository.update_problem(
            db=db,
            conversation=conversation,
            problem_statement=problem_statement,
        )

    @staticmethod
    def update_code(
        db: Session,
        session_id: str,
        user_id: str,
        user_code: str,
    ):
        conversation = ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        return ConversationRepository.update_code(
            db=db,
            conversation=conversation,
            user_code=user_code,
        )

    @staticmethod
    def append_message(
        db: Session,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
    ):
        # Verify that the session belongs to the user
        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        return ConversationRepository.add_message(
            db=db,
            session_id=session_id,
            role=role,
            content=content,
        )

    @staticmethod
    def get_messages(
        db: Session,
        session_id: str,
        user_id: str,
    ):
        # Verify ownership
        ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        return ConversationRepository.get_messages(
            db=db,
            session_id=session_id,
        )

    @staticmethod
    def delete_session(
        db: Session,
        session_id: str,
        user_id: str,
    ):
        conversation = ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        ConversationRepository.delete_session(
            db=db,
            conversation=conversation,
        )