from typing import Optional, List, Sequence, Dict, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import CrewMember, Airport, Aircraft
from backend.db.models.flight import Flight
from backend.db.models.crew_member_flight_assignment import crew_member_flight_assignment_assoc_table


class CrewMemberRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = CrewMember

    async def create(self, crew_member: dict) -> None:
        self.session.add(self.model(**crew_member))
        await self.session.commit()

    async def update(self, instance: "CrewMember") -> None:
        await self.session.merge(instance)
        await self.session.commit()

    async def get_all(
        self,
        eager_load: list = [],
        filters: dict = {},
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[Sequence["CrewMember"], int]:
        query = select(self.model)
        query = self._build_filter_query(query, filters)
        query = self._build_eager_load_query(query, eager_load)

        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        result = await self.session.execute(query.offset(skip).limit(limit))

        return result.scalars().all(), total

    async def get_by_id(self, employee_number: str, eager_load: list = []) -> Optional["CrewMember"]:
        query = select(self.model)
        query = self._build_eager_load_query(query, eager_load)
        result = await self.session.execute(query.where(self.model.employee_number == employee_number))

        return result.scalars().first()

    async def remove_flight(self, instance: 'CrewMember', flight: 'Flight'):  # type: ignore
        instance.flight_assignments.remove(flight)
        await self.session.commit()

    async def get_with_flight_assignments_asc(self, employee_number: str) -> 'CrewMember':
        query = (
            select(self.model)
            .join(
                crew_member_flight_assignment_assoc_table,
                self.model.id == crew_member_flight_assignment_assoc_table.c.crew_member_id
            )
            .join(
                Flight,
                Flight.id == crew_member_flight_assignment_assoc_table.c.flight_id
            )
            .where(self.model.employee_number == employee_number)
            .order_by(Flight.scheduled_arrival.asc())
            .options(contains_eager(self.model.flight_assignments))
        )

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_flight_assignments(self) -> Sequence['CrewMember']:
        query = (
            select(self.model)
            .join(
                crew_member_flight_assignment_assoc_table,
                self.model.id == crew_member_flight_assignment_assoc_table.c.crew_member_id
            )
            .join(
                Flight,
                Flight.id == crew_member_flight_assignment_assoc_table.c.flight_id
            )
            .order_by(Flight.scheduled_arrival.asc())
            .options(
                contains_eager(self.model.flight_assignments),
                selectinload(self.model.aircraft_qualifications)
            )
        )

        result = await self.session.execute(query)
        return result.scalars().unique().all()

    @staticmethod
    def _build_eager_load_query(query, eager_load: list):
        options = [
            *[selectinload(rel) for rel in eager_load],
        ]
        if options:
            query = query.options(*options)

        return query

    def _build_filter_query(self, query, filters: Dict[str, str | List[str]]):
        if not filters:
            return query

        base_airport = filters['base_airport']
        qualified_for = filters['qualified_for']

        if base_airport:
            query = query.join(self.model.base_airport).where(Airport.code == base_airport)
        if qualified_for:
            query = query.join(self.model.aircraft_qualifications).where(Aircraft.type.in_(qualified_for)) \
                .group_by(self.model.id) \
                .having(func.count(Aircraft.type) == len(qualified_for))

        return query