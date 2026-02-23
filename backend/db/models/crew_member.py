from collections import defaultdict
from typing import List, Optional, Dict

from sqlalchemy import String, ForeignKey, select, Sequence, Integer, UniqueConstraint, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from backend.db.models import Aircraft, Airport, Base
from backend.db.models.flight import Flight
from backend.db.models.crew_member_qualification import crew_member_aircraft_qualification_assoc_table
from backend.db.models.crew_member_flight_assignment import crew_member_flight_assignment_assoc_table
from backend.db.models.mixins import TimestampMixin


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
    flight_assignments: Mapped[List["Flight"]] = relationship(  # type: ignore
        secondary=crew_member_flight_assignment_assoc_table,
        back_populates='crew_members',
        order_by=asc(Flight.scheduled_departure)
    )

    def __repr__(self) -> str:
        return f'CrewMember(id={self.id}, employee_number={self.employee_number})'

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def daily_duty_hours(self) -> Dict[str, float]:
        hours_by_date = defaultdict(float)
        for flight in self.flight_assignments:
            if len(flight.duty_hours) == 1:
                hours_by_date[flight.scheduled_departure.date().isoformat()] += flight.duty_hours[0]
            else:
                hours_by_date[flight.scheduled_departure.date().isoformat()] += flight.duty_hours[0]
                hours_by_date[flight.scheduled_arrival.date().isoformat()] += flight.duty_hours[1]

        return hours_by_date
