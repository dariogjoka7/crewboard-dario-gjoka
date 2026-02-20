from typing import List, Optional

from sqlalchemy import String, ForeignKey, select, Sequence, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from backend.db.models.base import Base
from backend.db.models.crew_member_qualification import crew_member_aircraft_qualification_assoc_table
from backend.db.models.airport import Airport
from backend.db.models.aircraft import Aircraft
from backend.db.models.mixins import TimestampMixin


class CrewMember(Base, TimestampMixin):
    __tablename__ = 'crew_members'
    __table_args__ = (
        UniqueConstraint("employee_number", name="uq_crew_member_employee_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_number: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    base_airport_id: Mapped[int] = mapped_column(Integer, ForeignKey('airports.id'), nullable=False)

    base_airport: Mapped["Airport"] = relationship(back_populates='crew_members', lazy='select') # type: ignore
    aircraft_qualifications: Mapped[List["Aircraft"]] = relationship(  # type: ignore
        secondary=crew_member_aircraft_qualification_assoc_table
    )

    def __repr__(self) -> str:
        return f'CrewMember(id={self.id}, employee_number={self.employee_number})'

    @classmethod
    async def create(cls, session: Session, crew_member: dict) -> None:
        session.add(cls(**crew_member))
        session.commit()

    @classmethod
    async def get_all(cls, session: Session) -> Sequence["CrewMember"]:
        return session.scalars(select(cls)).all()

    @classmethod
    async def get_by_id(cls, session: Session, crew_member_id: str) -> Optional["CrewMember"]:
        return session.scalars(
            select(cls)
            .where(cls.employee_number == crew_member_id)
        ).first()
