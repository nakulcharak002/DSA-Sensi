from typing import List

from pydantic import BaseModel


class ReviewResponse(BaseModel):
    correct: bool
    score: int
    feedback: str
    logic: str
    bugs: List[str]
    edge_cases: List[str]
    readability: str
    optimization: List[str]