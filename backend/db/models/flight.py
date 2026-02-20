from datetime import datetime

from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from backend.db.models.base import Base
from backend.db.models.mixins import TimestampMixin


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
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=False))

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

    def __repr__(self) -> str:
        return f'Flight(id={self.id}, number={self.number})'
