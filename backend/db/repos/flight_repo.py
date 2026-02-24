from datetime import datetime, timezone

from typing import Sequence, Optional, Dict, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Flight, Airport, Aircraft


class FlightRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Flight

    async def create(self, flight: dict) -> None:
        self.session.add(self.model(**flight))
        await self.session.commit()

    async def get_all(
        self,
        eager_load: list = [],
        filters: dict = {},
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[Sequence["Flight"], int]:
        query = select(self.model)
        query = self._build_filter_query(query, filters)
        query = self._build_eager_load_query(query, eager_load)

        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        result = await self.session.execute(query.offset(skip).limit(limit))

        return result.scalars().all(), total

    async def get_by_number(self, number: str, eager_load: list = []) -> Optional["Flight"]:
        query = select(self.model)
        query = self._build_eager_load_query(query, eager_load)
        result = await self.session.execute(query.where(self.model.number == number))

        return result.scalars().first()

    @staticmethod
    def _build_eager_load_query(query, eager_load: list):
        options = [
            *[selectinload(rel) for rel in eager_load],
        ]
        if options:
            query = query.options(*options)

        return query

    def _build_filter_query(self, query, filters: Dict[str, datetime | str]):
        if not filters:
            return query

        scheduled_departure = filters['scheduled_departure']
        scheduled_arrival = filters['scheduled_arrival']
        departure_airport = filters['departure_airport']
        aircraft_type = filters['aircraft_type']

        if scheduled_departure:
            query = query.where(self.model.scheduled_departure == scheduled_departure.astimezone(timezone.utc))
        if scheduled_arrival:
            query = query.where(self.model.scheduled_arrival == scheduled_arrival.astimezone(timezone.utc))
        if departure_airport:
            query = query.join(self.model.departure_airport).where(Airport.code == departure_airport)
        if aircraft_type:
            query = query.join(self.model.aircraft).where(Aircraft.type == aircraft_type)

        return query
