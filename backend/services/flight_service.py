from typing import Dict, List

from datetime import datetime
from fastapi import Response, status, Request

from backend.db.repos.aircraft_repo import AircraftRepo
from backend.db.repos.airport_repo import AirportRepo
from backend.db.repos.flight_repo import FlightRepo
from backend.db.models import Flight
from backend.routers.models.flight.flight_create import FlightCreate
from backend.exceptions.custom_exceptions import NotFoundException, BadRequestException
from backend.routers.models.pagination import PaginationParams, build_pagination


class FlightService:
    def __init__(
        self,
        airport_repo: AirportRepo,
        aircraft_repo: AircraftRepo,
        flight_repo: FlightRepo
    ):
        self.airport_repo = airport_repo
        self.aircraft_repo = aircraft_repo
        self.flight_repo = flight_repo

    async def create_flight(self, body: FlightCreate) -> Response:
        existing_flight = await self.flight_repo.get_by_number(body.number)
        if existing_flight:
            raise BadRequestException(f'Flight with number {body.number} already exists')

        departure_airport = await self.airport_repo.get_by_code(body.departure_airport)
        if not departure_airport:
            raise NotFoundException(f'Departure airport with code {body.departure_airport} not found')

        arrival_airport = await self.airport_repo.get_by_code(body.arrival_airport)
        if not arrival_airport:
            raise NotFoundException(f'Arrival airport with code {body.arrival_airport} not found')

        aircraft = await self.aircraft_repo.get_by_type(body.aircraft)
        if not aircraft:
            raise NotFoundException(f'Aircraft with type {body.aircraft} not found')

        await self.flight_repo.create(
            {
                'number': body.number,
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'aircraft': aircraft,
                'scheduled_departure': body.scheduled_departure,
                'scheduled_arrival': body.scheduled_arrival
            }
        )

        return Response(status_code=status.HTTP_200_OK)

    async def list_all_flights(
        self,
        request: Request,
        pagination: PaginationParams,
        scheduled_departure: datetime | None,
        scheduled_arrival: datetime | None,
        departure_airport: str | None,
        aircraft_type: str | None
    ) -> dict:
        flights, total = await self.flight_repo.get_all(eager_load=[
            Flight.departure_airport,
            Flight.arrival_airport,
            Flight.aircraft
        ], filters={
            'scheduled_departure': scheduled_departure,
            'scheduled_arrival': scheduled_arrival,
            'departure_airport': departure_airport,
            'aircraft_type': aircraft_type
        },
            skip=pagination.skip,
            limit=pagination.limit
        )

        meta = build_pagination(request, pagination.page, pagination.limit, total)

        return {'data': flights, 'meta': meta}

    async def get_single_flight(self, number: str) -> Dict[str, List[Flight]]:
        flight = await self.flight_repo.get_by_number(number, eager_load=[
            Flight.departure_airport,
            Flight.arrival_airport,
            Flight.aircraft,
            Flight.crew_members
        ])

        if not flight:
            raise NotFoundException(f'Flight with number {number} not found')

        return {'data': [flight]}
