from typing import Any, List

from pydantic import Field, field_serializer

from backend.routers.models.flight.flight_response import FlightResponse


class FlightResponseWithAssignment(FlightResponse):
    crew_members: List[Any] = Field(
        description='The crew member assignments to this flight'
    )

    @field_serializer('crew_members')
    def serialize_crew_members(self, v) -> List[str]:
        return [cm.employee_number for cm in v]
