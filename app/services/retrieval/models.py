from pydantic import BaseModel, Field


class ProblemDocument(BaseModel):
    """
    Represents a coding problem stored in the vector database.
    """

    id: str
    title: str
    problem: str
    solution: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)


class RetrievedProblem(BaseModel):
    """
    Represents a retrieved problem along with its similarity score.
    """

    id: str
    score: float

    title: str
    problem: str
    solution: str

    difficulty: str
    tags: list[str] = Field(default_factory=list)