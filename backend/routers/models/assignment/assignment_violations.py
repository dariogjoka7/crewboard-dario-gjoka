from typing import List
from pydantic import BaseModel, Field


class AssignmentViolations(BaseModel):
    violations: List[str] = Field(
        description='Violations to the flight assignments'
    )
