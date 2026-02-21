from typing import List, Optional, Sequence

from sqlalchemy import String, Integer, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from backend.db.models.base import Base
from backend.db.models.mixins import TimestampMixin
from backend.db.models.crew_member_qualification import crew_member_aircraft_qualification_assoc_table


class Aircraft(Base, TimestampMixin):
    __tablename__ = 'aircrafts'
    __table_args__ = (
        UniqueConstraint('type', name='uq_aircraft_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)

    flights: Mapped[List["Flight"]] = relationship(back_populates="aircraft", lazy='select')  # type: ignore
    crew_members: Mapped[List["CrewMember"]] = relationship(  # type: ignore
        secondary=crew_member_aircraft_qualification_assoc_table,
        back_populates='aircraft_qualifications'
    )

    def __repr__(self) -> str:
        return f'Aircraft(id={self.id}, type={self.type})'

    @classmethod
    async def get_by_type(cls, session: AsyncSession, aircraft_type: str) -> Optional["Aircraft"]:
        result = await session.execute(select(cls).where(cls.type == aircraft_type))

        return result.scalars().first()

    @classmethod
    async def get_where_in(cls, session: AsyncSession, aircraft_types: List[str]) -> Sequence["Aircraft"]:
        result = await session.execute(select(cls).where(cls.type.in_(aircraft_types)))

        return result.scalars().all()
