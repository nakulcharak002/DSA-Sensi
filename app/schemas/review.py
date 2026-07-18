from pydantic import BaseModel
from typing import List

class ReviewResponse(BaseModel):
    logic: str
    bugs: List[str]
    edge_cases: List[str]
    readability: str
    optimization: List[str]
    score: str