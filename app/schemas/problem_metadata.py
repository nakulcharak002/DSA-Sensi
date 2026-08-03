from typing import List

from pydantic import BaseModel


class ProblemMetadata(BaseModel):
    title: str
    difficulty: str
    topics: List[str]