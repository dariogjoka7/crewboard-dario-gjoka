from typing import List
from pydantic import BaseModel


class Constraints(BaseModel):
    flight_number: str
    violations: List[str]


class ConstraintViolated(BaseModel):
    employee_number: str
    constraints: List[Constraints]


class AssignmentCheckResponse(BaseModel):
    violated_constraints: List[ConstraintViolated]
