import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, Query, Path

from backend.auth.dependencies import get_current_user
from backend.db.models.user import User
from backend.dependencies import get_assignment_service
from backend.routers.models.base import BaseMessageResponse
from backend.routers.models.assignment.assignment_create import AssignmentCreate
from backend.services.assignment_service import AssignmentService

router = APIRouter(prefix='/assignments', tags=['Assignments'])
logger = logging.getLogger()


@router.post(
    path='/',
    description='Assign crew members to flights',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to create crew member'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'One of the criterias has been violated'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def assign_crew_member_to_flight(
    _: Annotated[User, Depends(get_current_user)],
    assignment_service: Annotated[AssignmentService, Depends(get_assignment_service)],
    body: AssignmentCreate
):
    return await assignment_service.assign_crew_member_to_flight(body)


@router.delete(
    path='/',
    description='Assign crew members to flights',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to create crew member'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'One of the criterias has been violated'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def delete_flight_assignment(
    _: Annotated[User, Depends(get_current_user)],
    assignment_service: Annotated[AssignmentService, Depends(get_assignment_service)],
    employee_number: Annotated[str, Query(description='The employee number of the crew member')],
    flight_number: Annotated[str, Query(description='The number of the flight')]
):
    return await assignment_service.remove_assignment(employee_number, flight_number)


@router.get(
    path='/{employee_number}',
    description="Retrieve a crew member's full schedule",
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to get the full schedule'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Crew member not found'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def assign_crew_member_to_flight(
    _: Annotated[User, Depends(get_current_user)],
    assignment_service: Annotated[AssignmentService, Depends(get_assignment_service)],
    employee_number: Annotated[str, Path(example='E001', description='The employee number of the crew member')]
):
    return await assignment_service.get_full_schedule(employee_number)


@router.get(
    path='/healthcheck/',
    description="Check all the assignments and report any constraint violations found",
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to scan the assignments'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'No assignments found'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def assign_crew_member_to_flight(
    _: Annotated[User, Depends(get_current_user)],
    assignment_service: Annotated[AssignmentService, Depends(get_assignment_service)],
):
    return await assignment_service.check_assignments()


@router.post(
    path='/auto/',
    description='Auto assign the crew members to flights by respecting the constraints',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to auto assign the assignments'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'No assignments found'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def assign_crew_member_to_flight(
    _: Annotated[User, Depends(get_current_user)],
    assignment_service: Annotated[AssignmentService, Depends(get_assignment_service)],
):
    return await assignment_service.auto_assign_flights()
