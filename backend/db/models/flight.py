from datetime import datetime, timezone
from typing import Sequence, Dict, List, Optional, Tuple

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship, selectinload

from backend.db.models.base import Base
from backend.db.models.mixins import TimestampMixin
from backend.db.models import Aircraft, Airport
from backend.db.models.crew_member_flight_assignment import crew_member_flight_assignment_assoc_table


class Flight(Base, TimestampMixin):
    __tablename__ = 'flights'
    __table_args__ = (
        UniqueConstraint('number', name='uq_flight_number'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String, nullable=False)
    departure_airport_id: Mapped[int] = mapped_column(Integer, ForeignKey('airports.id'), nullable=False)
    arrival_airport_id: Mapped[int] = mapped_column(Integer, ForeignKey('airports.id'), nullable=False)
    aircraft_id: Mapped[int] = mapped_column(Integer, ForeignKey('aircrafts.id'), nullable=False)
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    departure_airport: Mapped["Airport"] = relationship(  # type: ignore
        foreign_keys=[departure_airport_id],
        back_populates='departures',
        lazy='select'
    )
    arrival_airport: Mapped["Airport"] = relationship(  # type: ignore
        foreign_keys=[arrival_airport_id],
        back_populates='arrivals',
        lazy='select'
    )
    aircraft: Mapped["Aircraft"] = relationship(back_populates='flights', lazy='select')  # type: ignore
    crew_members: Mapped[List["CrewMember"]] = relationship(  # type: ignore
        secondary=crew_member_flight_assignment_assoc_table,
        back_populates='flight_assignments'
    )

    def __repr__(self) -> str:
        return f'Flight(id={self.id}, number={self.number})'

    @property
    def duty_hours(self) -> Tuple[float, ...]:
        departure_date = self.scheduled_departure
        arrival_date = self.scheduled_arrival

        if departure_date.date() == arrival_date.date():
            return (arrival_date - departure_date).total_seconds() / 3600,

        departure_midnight = (departure_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        departure_hours = (departure_midnight - departure_date).total_seconds() / 3600

        arrival_midnight = arrival_date.replace(hour=0, minute=0, second=0, microsecond=0)
        arrival_hours = (arrival_date - arrival_midnight).total_seconds() / 3600

        return departure_hours, arrival_hours

    @classmethod
    async def create(cls, session: AsyncSession, flight: dict) -> None:
        session.add(cls(**flight))
        await session.commit()

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        eager_load: list = [],
        filters: dict | None = None,
        skip: int = 0,
        limit: int = 10
    ) -> Sequence["Flight"]:
        query = select(cls)
        query = cls._build_filter_query(query, filters)
        query = cls._build_eager_load_query(query, eager_load)
        result = await session.execute(query.offset(skip).limit(limit))

        return result.scalars().all()

    @classmethod
    async def get_by_number(cls, session: AsyncSession, number: str, eager_load: list = []) -> Optional["Flight"]:
        query = select(cls)
        query = cls._build_eager_load_query(query, eager_load)
        result = await session.execute(query.where(cls.number == number))

        return result.scalars().first()

    @classmethod
    def _build_eager_load_query(cls, query, eager_load: list):
        options = [
            *[selectinload(rel) for rel in eager_load],
        ]
        if options:
            query = query.options(*options)

        return query

    @classmethod
    def _build_filter_query(cls, query, filters: Dict[str, datetime | str]):
        scheduled_departure = filters['scheduled_departure']
        scheduled_arrival = filters['scheduled_arrival']
        departure_airport = filters['departure_airport']
        aircraft_type = filters['aircraft_type']

        if scheduled_departure:
            query = query.where(cls.scheduled_departure == scheduled_departure.astimezone(timezone.utc))
        if scheduled_arrival:
            query = query.where(cls.scheduled_arrival == scheduled_arrival.astimezone(timezone.utc))
        if departure_airport:
            query = query.join(cls.departure_airport).where(Airport.code == departure_airport)
        if aircraft_type:
            query = query.join(cls.aircraft).where(Aircraft.type == aircraft_type)

        return query
