from typing import Optional, List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Airport

class AirportRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Airport

    async def get_by_code(self, code: str) -> Optional["Airport"]:
        result = await self.session.execute(select(self.model).where(self.model.code == code))

        return result.scalars().first()

    async def get_where_in(self, codes: List[str]) -> Sequence["Airport"]:
        result = await self.session.execute(select(self.model).where(self.model.code.in_(codes)))

        return result.scalars().all()
