from fastapi import FastAPI
from pydantic import BaseModel
import logfire

from app.services.chat_service import ChatService

app = FastAPI(title="DSA Sensei")

logfire.configure()

sessions: dict[str, int] = {}


class HintRequest(BaseModel):
    session_id: str
    problem_statement: str
    stuck: bool = False


class HintResponse(BaseModel):
    response: str
    hint_level: int


@app.get("/")
def home():
    return {
        "status": "running",
        "project": "DSA Sensei",
    }


@app.post("/hint", response_model=HintResponse)
def request_hint(req: HintRequest):

    with logfire.span("Hint Request"):

        if req.session_id not in sessions:
            sessions[req.session_id] = 0

        elif req.stuck:
            sessions[req.session_id] += 1

        response = ChatService.get_hint(
            session_id=req.session_id,
            problem_statement=req.problem_statement,
            hint_level=sessions[req.session_id],
        )

        return HintResponse(
            response=response,
            hint_level=sessions[req.session_id],
        )


@app.post("/reset/{session_id}")
def reset_session(session_id: str):

    sessions.pop(session_id, None)

    return {
        "status": "reset"
    }