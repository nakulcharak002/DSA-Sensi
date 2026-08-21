from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Session as Conversation
from app.database.models import Message


class ConversationRepository:

    @staticmethod
    def create_session(
        db: Session,
        user_id: str,
        problem_statement: str = "",
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            problem_statement=problem_statement,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_session(
        db: Session,
        session_id: str,
        user_id: str,
    ) -> Conversation | None:

        statement = select(Conversation).where(
            Conversation.id == session_id,
            Conversation.user_id == user_id,
        )

        return db.scalar(statement)

    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: str,
    ) -> list[Conversation]:

        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def update_problem(
        db: Session,
        conversation: Conversation,
        problem_statement: str,
    ) -> Conversation:

        conversation.problem_statement = problem_statement

        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def add_message(
        db: Session,
        session_id: str,
        role: str,
        content: str,
    ) -> Message:

        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        session_id: str,
    ) -> list[Message]:

        statement = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def delete_session(
        db: Session,
        conversation: Conversation,
    ) -> None:

        db.delete(conversation)
        db.commit()