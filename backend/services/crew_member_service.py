from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response, Request, status

from backend.db.models.crew_member import CrewMember, Airport, Aircraft
from backend.db.repos.aircraft_repo import AircraftRepo
from backend.db.repos.airport_repo import AirportRepo
from backend.db.repos.crew_member_repo import CrewMemberRepo
from backend.exceptions.custom_exceptions import NotFoundException, BadRequestException
from backend.routers.models.base import CommonQueryParams
from backend.routers.models.crew_member.crew_member_body import CrewMemberBody
from backend.routers.models.crew_member.crew_member_update import CrewMemberUpdate
from backend.routers.models.pagination import PaginationParams, build_pagination


class CrewMemberService:
    def __init__(
        self,
        airport_repo: AirportRepo,
        aircraft_repo: AircraftRepo,
        crew_member_repo: CrewMemberRepo
    ):
        self.airport_repo = airport_repo
        self.aircraft_repo = aircraft_repo
        self.crew_member_repo = crew_member_repo

    async def create_crew_member(self, body: CrewMemberBody):
        existing_crew_member = await self.crew_member_repo.get_by_id(body.employee_number)
        if existing_crew_member:
            raise BadRequestException(f'Crew member with employee number {body.employee_number} exists')

        base_airport = await self.airport_repo.get_by_code(body.base_airport)
        if not base_airport:
            raise NotFoundException('Airport with does not exist on our db')

        aircrafts = await self.aircraft_repo.get_where_in(body.aircraft_qualifications)
        aircraft_types = [ac.type for ac in aircrafts]
        missing = []
        for aircraft_type in set(body.aircraft_qualifications):
            if aircraft_type not in aircraft_types:
                missing.append(f'Aircraft {aircraft_type} qualification is missing')

        if missing:
            raise NotFoundException(', '.join(missing))

        await self.crew_member_repo.create({
            'employee_number': body.employee_number,
            'first_name': body.first_name,
            'last_name': body.last_name,
            'email': body.email,
            'base_airport': base_airport,
            'aircraft_qualifications': aircrafts
        })

        return Response(status_code=status.HTTP_200_OK)

    async def update_existing_crew_member(self, employee_number: str, body: CrewMemberUpdate):
        crew_member = await self.crew_member_repo.get_by_id(employee_number, eager_load=[
            CrewMember.base_airport,
            CrewMember.aircraft_qualifications
        ])
        if not crew_member:
            raise NotFoundException(f'Crew member with employee number {employee_number} not found')

        if body.first_name is not None:
            crew_member.first_name = body.first_name
        if body.last_name is not None:
            crew_member.last_name = body.last_name
        if body.email is not None:
            crew_member.email = body.email

        if body.base_airport is not None:
            base_airport = await self.airport_repo.get_by_code(body.base_airport)
            if not base_airport:
                raise NotFoundException(f'Airport with code {body.base_airport} not found')
            crew_member.base_airport = base_airport

        if body.aircraft_qualifications is not None:
            aircraft_qualifications = await self.aircraft_repo.get_where_in(body.aircraft_qualifications)
            aircraft_types = [ac.type for ac in aircraft_qualifications]
            missing = []
            for aircraft_type in set(body.aircraft_qualifications):
                if aircraft_type not in aircraft_types:
                    missing.append(f'Aircraft {aircraft_type} qualification is missing')

            if missing:
                raise NotFoundException(', '.join(missing))

            crew_member.aircraft_qualifications = aircraft_qualifications

        await self.crew_member_repo.update(crew_member)

        return Response(status_code=status.HTTP_200_OK)

    async def list_all_crew_members(
        self,
        request: Request,
        pagination: PaginationParams,
        base_airport: str | None,
        qualified_for: List[str]
    ):
        crew_members, total = await self.crew_member_repo.get_all(eager_load=[
            CrewMember.base_airport,
            CrewMember.aircraft_qualifications
        ], filters={
            'base_airport': base_airport,
            'qualified_for': qualified_for
        },
            skip=pagination.skip,
            limit=pagination.limit
        )

        meta = build_pagination(request, pagination.page, pagination.limit, total)

        return {'data': crew_members, 'meta': meta}

    async def get_one_crew_member(self, employee_number: str):
        crew_member = await self.crew_member_repo.get_by_id(employee_number, eager_load=[
            CrewMember.base_airport,
            CrewMember.aircraft_qualifications
        ])

        if not crew_member:
            raise NotFoundException(f'Crew member with employee number {employee_number} not found')

        return {'data': [crew_member]}
