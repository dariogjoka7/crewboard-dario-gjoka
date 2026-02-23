from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AssignmentFullSchedule(BaseModel):
    number: str | None = Field(
        default=None,
        examples=['F1'],
        description='The number of the flight',
        min_length=2
    )
    from_time: datetime = Field(
        description='The date and time of the departure in UTC',
        serialization_alias='from'
    )
    to: datetime = Field(
        description='THe date and time of the arrival in UTC'
    )
    rest_time: bool = Field(
        default=True,
        description='Indicates if the crew member is on duty time or during rest time'
    )