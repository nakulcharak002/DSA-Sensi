from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import User


class UserRepository:

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:

        statement = select(User).where(
            User.email == email
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: str,
    ) -> User | None:

        statement = select(User).where(
            User.id == user_id
        )

        return db.scalar(statement)

    @staticmethod
    def create(
        db: Session,
        email: str,
        password_hash: str,
    ) -> User:

        user = User(
            email=email,
            password_hash=password_hash,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
