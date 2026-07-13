from typing import Literal
from pydantic import BaseModel
from typing import Literal

class SupervisorDecision(BaseModel):
    next_node: Literal[
        "hint",
        "review",
        "complexity",
        "execution",
    ]