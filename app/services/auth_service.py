from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.auth.security import hash_password, verify_password, create_access_token


class AuthService:

    @staticmethod
    def register(
        db: Session,
        email: str,
        password: str,
    ):
        existing_user = UserRepository.get_by_email(
            db,
            email,
        )

        if existing_user:
            raise ValueError("User already exists")

        hashed_password = hash_password(password)

        user = UserRepository.create(
            db=db,
            email=email,
            password_hash=hashed_password,
        )

        return user

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):

        user = UserRepository.get_by_email(
            db,
            email,
        )

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            user.id,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
        }
