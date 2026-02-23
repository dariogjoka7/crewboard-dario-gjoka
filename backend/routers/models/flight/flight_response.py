from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: str = Field(
        examples=['F1'],
        description='The number of the flight',
        min_length=2
    )
    departure_airport: Any = Field(
        description='The IATA code of the airport from which the aircraft will departure',
    )
    arrival_airport: Any = Field(
        description='The IATA code of the airport where the aircraft will arrive'
    )
    aircraft: Any = Field(
        description='The code of the aircraft',
    )
    scheduled_departure: datetime = Field(
        description='The date and time of the departure in UTC'
    )
    scheduled_arrival: datetime = Field(
        description='THe date and time of the arrival in UTC'
    )

    @field_serializer('departure_airport')
    def serialize_departure_airport(self, v):
        return v.code

    @field_serializer('arrival_airport')
    def serialize_arrival_airport(self, v):
        return v.code

    @field_serializer('aircraft')
    def serialize_aircraft(self, v):
        return v.type
