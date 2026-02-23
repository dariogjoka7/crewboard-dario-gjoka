from pydantic import BaseModel


class AssignedFlight(BaseModel):
    flight_number: str
    assigned_to: str
    name: str


class UnassignableReason(BaseModel):
    employee_number: str
    reason: str


class FailedFlight(BaseModel):
    flight_number: str
    unassignable_reasons: list[UnassignableReason]


class CrewDutySummary(BaseModel):
    employee_number: str
    name: str
    total_duty_hours: float


class AssignmentAutoResponse(BaseModel):
    assigned: list[AssignedFlight]
    failed: list[FailedFlight]
    duty_summary: list[CrewDutySummary]
    fairness_gap_hours: float
