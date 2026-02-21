import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Response, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from backend.dependencies import get_session_dep

from backend.routers.models.base import BaseMessageResponse, BaseListResponse
from routers.models.base import CommonQueryParams
from routers.models.crew_member.crew_member_body import CrewMemberBody
from backend.db.models.crew_member import CrewMember, Airport, Aircraft
from routers.models.crew_member.crew_member_response import CrewMemberResponse
from routers.models.crew_member.crew_member_update import CrewMemberUpdate

router = APIRouter(prefix='/crew_members', tags=['Crew Members'])
logger = logging.getLogger()

SessionDep = Annotated[AsyncSession, Depends(get_session_dep)]


@router.post(
    path='/',
    description='For creating new crew members',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to create crew member'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Could not find airport'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def create_crew_member(
    body: CrewMemberBody,
    session: SessionDep
):
    logger.info(f'Creating new crew member: {body.first_name} {body.last_name}')
    base_airport = await Airport.get_by_code(session, body.base_airport)
    if not base_airport:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': 'Airport does not exist on our db'
            }
        )

    aircrafts = await Aircraft.get_where_in(session, body.aircraft_qualifications)
    aircraft_types = [ac.type for ac in aircrafts]
    missing = []
    for aircraft_type in set(body.aircraft_qualifications):
        if aircraft_type not in aircraft_types:
            missing.append(f'Aircraft {aircraft_type} qualification is missing')

    if missing:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': ', '.join(missing)
            }
        )

    await CrewMember.create(session, {
        'employee_number': body.employee_number,
        'first_name': body.first_name,
        'last_name': body.last_name,
        'email': body.email,
        'base_airport': base_airport,
        'aircraft_qualifications': aircrafts
    })

    return Response(status_code=status.HTTP_200_OK)


@router.patch(
    path='/{employee_number}',
    description='For updating an existing crew member',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to create crew member'},
        status.HTTP_404_NOT_FOUND: {'model': BaseMessageResponse, 'description': 'Could not find airport'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def update_existing_crew_member(
    session: SessionDep,
    employee_number: Annotated[str, Path(description='The employee number of the crew member we want to update')],
    body: CrewMemberUpdate,
):
    logger.info(f'Updating crew member with employee_number: {employee_number}')
    crew_member = await CrewMember.get_by_id(session, employee_number, eager_load=[
        CrewMember.base_airport,
        CrewMember.aircraft_qualifications
    ])
    if not crew_member:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f'Crew member with employee number {employee_number} does not exist'}
        )

    crew_member.first_name = crew_member.first_name
    crew_member.last_name = crew_member.last_name
    crew_member.email = crew_member.email

    base_airport = await Airport.get_by_code(session, body.base_airport)
    if base_airport:
        crew_member.base_airport = base_airport

    aircraft_qualifications = await Aircraft.get_where_in(session, body.aircraft_qualifications)
    if aircraft_qualifications:
        crew_member.aircraft_qualifications = aircraft_qualifications

    await CrewMember.update(session, crew_member)

    return Response(status_code=status.HTTP_200_OK)


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
    session: SessionDep,
    query_params: Annotated[CommonQueryParams, Depends()],
    base_airport: Annotated[str | None, Query(max_length=4, description='The base airport of the crew member')] = None,
    qualified_for: Annotated[List[str], Query(description='The list of aircraft qualifications of the crew member')] = [],
):
    logger.info('Listing all crew members')

    crew_members = await CrewMember.get_all(session, eager_load=[
        CrewMember.base_airport,
        CrewMember.aircraft_qualifications
    ], filters={
        'base_airport': base_airport,
        'qualified_for': qualified_for
    },
        skip=query_params.skip,
        limit=query_params.limit
    )

    return {'data': crew_members, 'meta': query_params}


@router.get(
    path='/{employee_number}',
    description='For retrieving a crew member by their employee number',
    response_model=BaseListResponse[CrewMemberResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': BaseMessageResponse, 'description': 'Failed to list crew members'},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': BaseMessageResponse, 'description': 'Internal server error'}
    }
)
async def get_crew_member_by_number(
    employee_number: Annotated[str, Path(description='The employee number')],
    session: SessionDep
):
    logger.info(f'Getting crew member with id: {employee_number}')
    crew_member = await CrewMember.get_by_id(session, employee_number, eager_load=[
        CrewMember.base_airport,
        CrewMember.aircraft_qualifications
    ])

    return {'data': [crew_member]}
