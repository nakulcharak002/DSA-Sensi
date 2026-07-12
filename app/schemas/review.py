from pydantic import BaseModel
from typing import List


class ReviewResponse(BaseModel):
    logic: str
    bugs: List[str]
    edge_cases: List[str]
    time_complexity: str
    space_complexity: str
    readability: str