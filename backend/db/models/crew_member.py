from typing import List, Optional, Dict

from sqlalchemy import String, ForeignKey, select, Sequence, Integer, UniqueConstraint, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload, with_loader_criteria

from backend.db.models.base import Base
from backend.db.models.crew_member_qualification import crew_member_aircraft_qualification_assoc_table
from backend.db.models.airport import Airport
from backend.db.models.aircraft import Aircraft
from backend.db.models.mixins import TimestampMixin
from routers.models.crew_member.crew_member_update import CrewMemberUpdate


class CrewMember(Base, TimestampMixin):
    __tablename__ = 'crew_members'
    __table_args__ = (
        UniqueConstraint('employee_number', name="uq_crew_member_employee_number"),
        UniqueConstraint('email', name='uq_crew_member_email')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_number: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    base_airport_id: Mapped[int] = mapped_column(Integer, ForeignKey('airports.id'), nullable=False)

    base_airport: Mapped["Airport"] = relationship(back_populates='crew_members', lazy='select')  # type: ignore
    aircraft_qualifications: Mapped[List["Aircraft"]] = relationship(  # type: ignore
        secondary=crew_member_aircraft_qualification_assoc_table,
        back_populates='crew_members'
    )

    def __repr__(self) -> str:
        return f'CrewMember(id={self.id}, employee_number={self.employee_number})'

    @classmethod
    async def create(cls, session: AsyncSession, crew_member: dict) -> None:
        session.add(cls(**crew_member))
        await session.commit()

    @staticmethod
    async def update(session: AsyncSession, instance: "CrewMember") -> None:
        await session.merge(instance)
        await session.commit()

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        eager_load: list = [],
        filters: dict | None = None,
        skip: int = 0,
        limit: int = 10
    ) -> Sequence["CrewMember"]:
        query = select(cls)
        query = cls._build_filter_query(query, filters)
        query = cls._build_eager_load_query(query, eager_load)
        result = await session.execute(query.offset(skip).limit(limit))

        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, employee_number: str, eager_load: list = []) -> Optional["CrewMember"]:
        query = select(cls)
        query = cls._build_eager_load_query(query, eager_load)
        result = await session.execute(query.where(cls.employee_number == employee_number))

        return result.scalars().first()

    @classmethod
    def _build_eager_load_query(cls, query, eager_load: list):
        options = [
            *[selectinload(relationship) for relationship in eager_load],
        ]
        if options:
            query = query.options(*options)

        return query

    @classmethod
    def _build_filter_query(cls, query, filters: Dict[str, str | List[str]]):
        base_airport = filters['base_airport']
        qualified_for = filters['qualified_for']

        if base_airport:
            query = query.join(cls.base_airport).where(Airport.code == base_airport)
        if qualified_for:
            query = query.join(cls.aircraft_qualifications).where(Aircraft.type.in_(qualified_for)) \
                          .group_by(cls.id) \
                          .having(func.count(Aircraft.type) == len(qualified_for))

        return query
