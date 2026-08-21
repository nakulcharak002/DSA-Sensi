from app.database.connection import SessionLocal
from app.repositories.conversation_repository import ConversationRepository


def main():

    db = SessionLocal()

    try:

        # Temporary test user.
        user_id = "test-user-123"

        conversation = ConversationRepository.create_session(
            db=db,
            user_id=user_id,
            problem_statement="Two Sum",
        )

        print("Created session:")
        print(conversation.id)

        fetched = ConversationRepository.get_session(
            db=db,
            session_id=conversation.id,
            user_id=user_id,
        )

        print("\nFetched session:")
        print(fetched.id if fetched else None)

        ConversationRepository.add_message(
            db=db,
            session_id=conversation.id,
            role="user",
            content="I am stuck on Two Sum.",
        )

        ConversationRepository.add_message(
            db=db,
            session_id=conversation.id,
            role="assistant",
            content="Think about using a hash map.",
        )

        messages = ConversationRepository.get_messages(
            db=db,
            session_id=conversation.id,
        )

        print("\nMessages:")

        for message in messages:
            print(message.role, ":", message.content)

        sessions = ConversationRepository.get_user_sessions(
            db=db,
            user_id=user_id,
        )

        print("\nUser sessions:")
        print(len(sessions))

    finally:
        db.close()


if __name__ == "__main__":
    main()