from pydantic import BaseModel


class ComplexityResponse(BaseModel):
    time_complexity: str
    space_complexity: str
    optimal: bool
    explanation: str