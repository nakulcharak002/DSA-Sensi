from typing import TypedDict, List, Literal


class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class AgentState(TypedDict):

    session_id: str

    messages: List[Message]

    conversation_history: List[Message]

    problem_statement: str

    user_code: str

    request_type: str

    hint_level: int

    next_node: str

    last_agent: str

    response: str

    review: dict

    complexity: dict

    execution_result: dict

    retrieved_problems: list[dict]