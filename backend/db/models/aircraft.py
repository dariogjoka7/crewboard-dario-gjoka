from typing import List

from sqlalchemy import String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base
from backend.db.models.mixins import TimestampMixin


class Aircraft(Base, TimestampMixin):
    __tablename__ = 'aircrafts'
    __table_args__ = (
        UniqueConstraint('type', name='uq_aircraft_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)

    flights: Mapped[List["Flight"]] = relationship(back_populates="aircraft", lazy='select')  # type: ignore

    def __repr__(self) -> str:
        return f'Aircraft(id={self.id}, type={self.type})'
