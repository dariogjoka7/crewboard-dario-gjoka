from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response, status

from backend.db.models.crew_member import CrewMember, Airport, Aircraft
from db.repos.aircraft_repo import AircraftRepo
from db.repos.airport_repo import AirportRepo
from db.repos.crew_member_repo import CrewMemberRepo
from exceptions.custom_exceptions import NotFoundException
from routers.models.base import CommonQueryParams
from routers.models.crew_member.crew_member_body import CrewMemberBody
from routers.models.crew_member.crew_member_update import CrewMemberUpdate


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
        base_airport = await self.airport_repo.get_by_code(body.base_airport)
        if not base_airport:
            raise NotFoundException('Airport with does not exist on our db')

        aircrafts = await self.airport_repo.get_where_in(body.aircraft_qualifications)
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

        crew_member.first_name = crew_member.first_name
        crew_member.last_name = crew_member.last_name
        crew_member.email = crew_member.email

        base_airport = await self.airport_repo.get_by_code(body.base_airport)
        if not base_airport:
            raise NotFoundException(f'Airport with code {body.base_airport} not found')

        crew_member.base_airport = base_airport

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

    async def list_all_crew_members(self, query_params: CommonQueryParams, base_airport: str | None, qualified_for: List[str]):
        crew_members = await self.crew_member_repo.get_all(eager_load=[
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

    async def get_one_crew_member(self, employee_number: str):
        crew_member = await self.crew_member_repo.get_by_id(employee_number, eager_load=[
            CrewMember.base_airport,
            CrewMember.aircraft_qualifications
        ])

        return {'data': [crew_member]}
