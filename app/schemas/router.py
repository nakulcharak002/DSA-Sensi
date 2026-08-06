from typing import Literal
from pydantic import BaseModel


class SupervisorDecision(BaseModel):
    next_node: Literal[
        "hint",
        "review",
        "complexity",
        "execution",
    ]

    increase_hint: bool = False