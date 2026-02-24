import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_session_dep
from backend.dependencies import get_crew_member_service

from backend.auth.dependencies import get_current_user
from backend.db.models.user import User
from backend.routers.models.base import BaseMessageResponse, BaseListResponse
from backend.routers.models.base import CommonQueryParams
from backend.routers.models.crew_member.crew_member_body import CrewMemberBody
from backend.routers.models.crew_member.crew_member_response import CrewMemberResponse
from backend.routers.models.crew_member.crew_member_update import CrewMemberUpdate
from backend.services.crew_member_service import CrewMemberService
from backend.routers.models.pagination import PaginationParams

router = APIRouter(prefix='/crew_members', tags=['Crew Members'])
logger = logging.getLogger()


@router.post(
    path='/',
    description='For creating new crew members',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Crew member exists'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Could not find airport'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def create_crew_member(
    _: Annotated[User, Depends(get_current_user)],
    body: CrewMemberBody,
    crew_member_service: Annotated[CrewMemberService, Depends(get_crew_member_service)]
):
    logger.info(f'Creating new crew member: {body.first_name} {body.last_name}')
    return await crew_member_service.create_crew_member(body)

@router.patch(
    path='/{employee_number}',
    description='For updating an existing crew member',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to update crew member'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Could not find crew member or airport'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def update_existing_crew_member(
    _: Annotated[User, Depends(get_current_user)],
    employee_number: Annotated[str, Path(description='The employee number of the crew member we want to update')],
    body: CrewMemberUpdate,
    crew_member_service: Annotated[CrewMemberService, Depends(get_crew_member_service)]
):
    logger.info(f'Updating crew member with employee_number: {employee_number}')
    return await crew_member_service.update_existing_crew_member(employee_number, body)


@router.get(
    path='/',
    description='For listing crew members',
    response_model=BaseListResponse[CrewMemberResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to list crew members'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def list_crew_members(
    _: Annotated[User, Depends(get_current_user)],
    crew_member_service: Annotated[CrewMemberService, Depends(get_crew_member_service)],
    request: Request,
    pagination: Annotated[PaginationParams, Depends()],
    base_airport: Annotated[str | None, Query(max_length=4, description='The base airport of the crew member')] = None,
    qualified_for: Annotated[List[str], Query(description='The list of aircraft qualifications of the crew member')] = [],
):
    logger.info('Listing all crew members')
    return await crew_member_service.list_all_crew_members(request, pagination, base_airport, qualified_for)


@router.get(
    path='/{employee_number}',
    description='For retrieving a crew member by their employee number',
    response_model=BaseListResponse[CrewMemberResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Could not find crew member'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def get_crew_member_by_number(
    _: Annotated[User, Depends(get_current_user)],
    crew_member_service: Annotated[CrewMemberService, Depends(get_crew_member_service)],
    employee_number: Annotated[str, Path(description='The employee number')],
):
    logger.info(f'Getting crew member with id: {employee_number}')
    return await crew_member_service.get_one_crew_member(employee_number)

