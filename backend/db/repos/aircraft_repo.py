from typing import Optional, List, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Aircraft


class AircraftRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Aircraft

    async def get_by_type(self, aircraft_type: str) -> Optional["Aircraft"]:
        result = await self.session.execute(select(self.model).where(self.model.type == aircraft_type))

        return result.scalars().first()

    async def get_where_in(self, aircraft_types: List[str]) -> Sequence["Aircraft"]:
        result = await self.session.execute(select(self.model).where(self.model.type.in_(aircraft_types)))

        return result.scalars().all()
