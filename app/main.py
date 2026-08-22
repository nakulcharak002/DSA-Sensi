from contextlib import asynccontextmanager
from typing import Any

import logfire
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.routes.session_routes import router as session_router
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.services.chat_service import ChatService
from app.guardrails.initializer import initialize_rails
from app.routes.auth import router as auth_router


# ---------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_rails()
    yield


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="DSA Sensei",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(session_router)

logfire.configure()


# =========================================================
# REQUEST / RESPONSE MODELS
# =========================================================


class HintRequest(BaseModel):
    session_id: str
    problem_statement: str
    stuck: bool = False


class HintResponse(BaseModel):
    response: str
    hint_level: int


class ExecuteRequest(BaseModel):
    session_id: str
    problem_statement: str
    user_code: str


class ExecuteResponse(BaseModel):
    compiled: bool
    stdout: str
    stderr: str
    exit_code: int


class ReviewRequest(BaseModel):
    session_id: str
    problem_statement: str
    user_code: str


class ReviewResponse(BaseModel):
    review: dict


class ComplexityRequest(BaseModel):
    session_id: str
    problem_statement: str
    user_code: str


class ComplexityResponse(BaseModel):
    complexity: dict


class ChatRequest(BaseModel):
    session_id: str
    message: str
    problem_statement: str = ""
    user_code: str = ""


class ChatResponse(BaseModel):
    response: Any


# =========================================================
# HOME
# =========================================================


@app.get("/")
def home():
    return {
        "status": "running",
        "project": "DSA Sensei",
    }


# =========================================================
# HINT
# =========================================================


@app.post("/hint", response_model=HintResponse)
def request_hint(
    req: HintRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    with logfire.span("Hint Request"):

        # For now we keep hint_level local to this request.
        # Later we can persist it in the Session table if needed.
        hint_level = 1 if req.stuck else 0

        response = ChatService.get_hint(
            db=db,
            user_id=current_user.id,
            session_id=req.session_id,
            problem_statement=req.problem_statement,
            hint_level=hint_level,
        )

        return HintResponse(
            response=response,
            hint_level=hint_level,
        )


# =========================================================
# EXECUTE
# =========================================================


@app.post("/execute", response_model=ExecuteResponse)
def execute_code(
    req: ExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    with logfire.span("Execute Code"):

        result = ChatService.execute_code(
            db=db,
            user_id=current_user.id,
            session_id=req.session_id,
            problem_statement=req.problem_statement,
            user_code=req.user_code,
        )

        return ExecuteResponse(**result)


# =========================================================
# REVIEW
# =========================================================


@app.post("/review", response_model=ReviewResponse)
def review_code(
    req: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    with logfire.span("Review Code"):

        result = ChatService.review_code(
            db=db,
            user_id=current_user.id,
            session_id=req.session_id,
            problem_statement=req.problem_statement,
            user_code=req.user_code,
        )

        return ReviewResponse(
            review=result,
        )


# =========================================================
# COMPLEXITY
# =========================================================


@app.post("/complexity", response_model=ComplexityResponse)
def analyze_complexity(
    req: ComplexityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    with logfire.span("Complexity Analysis"):

        result = ChatService.analyze_complexity(
            db=db,
            user_id=current_user.id,
            session_id=req.session_id,
            problem_statement=req.problem_statement,
            user_code=req.user_code,
        )

        return ComplexityResponse(
            complexity=result,
        )


# =========================================================
# CHAT
# =========================================================


@app.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    with logfire.span("Supervisor Chat"):

        response = ChatService.chat(
            db=db,
            user_id=current_user.id,
            session_id=req.session_id,
            message=req.message,
            problem_statement=req.problem_statement,
            user_code=req.user_code,
        )

        return ChatResponse(
            response=response,
        )


# =========================================================
# RESET SESSION
# =========================================================


@app.post("/reset/{session_id}")
def reset_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    from app.services.conversation_service import ConversationService

    ConversationService.delete_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    return {
        "status": "reset",
    }