from datetime import date, datetime, timezone

from pydantic import BaseModel, Field, ConfigDict, model_validator


class FlightCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    number: str = Field(
        examples=['F1'],
        description='The number of the flight',
        min_length=2
    )
    departure_airport: str = Field(
        examples=['FRA'],
        description='The IATA code of the airport from which the aircraft will departure',
        min_length=2
    )
    arrival_airport: str = Field(
        examples=['LIS'],
        description='The IATA code of the airport where the aircraft will arrive'
    )
    aircraft: str = Field(
        examples=['A320'],
        description='The code of the aircraft',
        min_length=4
    )
    scheduled_departure: datetime = Field(
        examples=['2026-02-01T06:00:00Z'],
        description='The date of the departure in UTC'
    )
    scheduled_arrival: datetime = Field(
        examples=['2026-02-01T08:00:00Z'],
        description='THe date of the arrival in UTC'
    )

    @model_validator(mode='after')
    def departure_not_equal_arrival(self) -> 'FlightCreate':
        if self.departure_airport == self.arrival_airport:
            raise ValueError('Departure airport and arrival airport cannot be the same!')

        return self

    @model_validator(mode="after")
    def zero_seconds(self) -> 'FlightCreate':
        self.scheduled_departure = self.scheduled_departure.replace(second=0, microsecond=0, tzinfo=timezone.utc)
        self.scheduled_arrival = self.scheduled_arrival.replace(second=0, microsecond=0, tzinfo=timezone.utc)

        if self.scheduled_departure >= self.scheduled_arrival:
            raise ValueError('Scheduled departure cannot be after scheduled arrival')

        return self
