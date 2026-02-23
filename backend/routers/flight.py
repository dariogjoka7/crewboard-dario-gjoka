from datetime import datetime
from typing import Annotated
import logging

from fastapi import APIRouter, Depends, status, Query, Path

from backend.auth.dependencies import get_current_user
from backend.db.models.user import User
from backend.dependencies import get_flight_service
from backend.routers.models.base import BaseMessageResponse
from routers.models.base import CommonQueryParams, BaseListResponse
from routers.models.flight.flight_create import FlightCreate
from routers.models.flight.flight_response import FlightResponse
from routers.models.flight.flight_response_with_assignments import FlightResponseWithAssignment
from services.flight_service import FlightService

router = APIRouter(prefix='/flights', tags=['Flights'])
logger = logging.getLogger()

@router.post(
    path='/',
    description='For creating a flight',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to create flight'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Could not find airport'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def create_flight(
    _: Annotated[User, Depends(get_current_user)],
    flight_service: Annotated[FlightService, Depends(get_flight_service)],
    body: FlightCreate
):
    logger.info(f"Creating a new flight with number: {body.number}")
    return await flight_service.create_flight(body)

@router.get(
    path='/',
    description='For listing crew members',
    response_model=BaseListResponse[FlightResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to list crew members'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def list_flights(
    _: Annotated[User, Depends(get_current_user)],
    flight_service: Annotated[FlightService, Depends(get_flight_service)],
    query_params: Annotated[CommonQueryParams, Depends()],
    scheduled_departure: Annotated[datetime | None, Query(description='The departure date and time of the flight')] = None,
    scheduled_arrival: Annotated[datetime | None, Query(description='The arrival date and time of the flight')] = None,
    departure_airport: Annotated[str | None, Query(description='The airport where the flight will departure from')] = None,
    aircraft_type: Annotated[str | None, Query(description='The aircraft type')] = None
):
    logger.info('Listing all flights')
    return await flight_service.list_all_flights(query_params, scheduled_departure, scheduled_arrival, departure_airport, aircraft_type)

@router.get(
    path='/{number}',
    description='For retrieving a flight by their number',
    response_model=BaseListResponse[FlightResponseWithAssignment],
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to list '},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def get_flight_by_number(
    _: Annotated[User, Depends(get_current_user)],
    flight_service: Annotated[FlightService, Depends(get_flight_service)],
    number: Annotated[str, Path(description='The employee number')]
):
    logger.info(f'Getting flight with number: {number}')
    return await flight_service.get_single_flight(number)

