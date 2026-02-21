from typing import List, Optional

from sqlalchemy import String, Integer, UniqueConstraint, select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from backend.db.models.base import Base
from backend.db.models.mixins import TimestampMixin


class Airport(Base, TimestampMixin):
    __tablename__ = 'airports'
    __table_args__ = (
        UniqueConstraint("code", name="uq_airport_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    crew_members: Mapped[List["CrewMember"]] = relationship(back_populates='base_airport', lazy='select') # type: ignore

    departures: Mapped[List["Flight"]] = relationship(  # type: ignore
        foreign_keys="Flight.departure_airport_id",
        back_populates='departure_airport',
        lazy='select'
    )
    arrivals: Mapped[List["Flight"]] = relationship(  # type: ignore
        foreign_keys='Flight.arrival_airport_id',
        back_populates='arrival_airport',
        lazy='select'
    )

    def __repr__(self) -> str:
        return f'Airport(id={self.id}, code={self.code})'

    @classmethod
    async def get_by_code(cls, session: AsyncSession, code: str) -> Optional["Airport"]:
        result = await session.execute(select(cls).where(cls.code == code))

        return result.scalars().first()

    @classmethod
    async def get_where_in(cls, session: AsyncSession, codes: List[str]) -> Sequence["Airport"]:
        result = await session.execute(select(cls).where(cls.code.in_(codes)))

        return result.scalars().all()
