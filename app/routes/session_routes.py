from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.services.conversation_service import ConversationService


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


# =========================================================
# Schemas
# =========================================================


class CreateSessionRequest(BaseModel):
    problem_statement: str = ""


class SessionResponse(BaseModel):
    session_id: str
    problem_statement: str | None
    user_code: str | None


class MessageResponse(BaseModel):
    role: str
    content: str


class SessionDetailResponse(BaseModel):
    session_id: str
    problem_statement: str | None
    user_code: str | None
    messages: list[MessageResponse]


# =========================================================
# CREATE SESSION
# =========================================================


@router.post(
    "",
    response_model=SessionResponse,
)
def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = ConversationService.create_session(
        db=db,
        user_id=current_user.id,
        problem_statement=request.problem_statement,
    )

    return SessionResponse(
        session_id=session.id,
        problem_statement=session.problem_statement,
        user_code=session.user_code,
    )


# =========================================================
# GET ALL SESSIONS FOR CURRENT USER
# =========================================================


@router.get(
    "",
    response_model=list[SessionResponse],
)
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = ConversationService.get_user_sessions(
        db=db,
        user_id=current_user.id,
    )

    return [
        SessionResponse(
            session_id=session.id,
            problem_statement=session.problem_statement,
            user_code=session.user_code,
        )
        for session in sessions
    ]


# =========================================================
# GET ONE SESSION + MESSAGES
# =========================================================


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = ConversationService.get_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )

        messages = ConversationService.get_messages(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return SessionDetailResponse(
        session_id=session.id,
        problem_statement=session.problem_statement,
        user_code=session.user_code,
        messages=[
            MessageResponse(
                role=message.role,
                content=message.content,
            )
            for message in messages
        ],
    )


# =========================================================
# DELETE SESSION
# =========================================================


@router.delete(
    "/{session_id}"
)
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ConversationService.delete_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return {
        "status": "deleted",
        "session_id": session_id,
    }