from sqlalchemy import Table, Column, ForeignKey

from backend.db.models.base import Base

crew_member_aircraft_qualification_assoc_table = Table(
    'crew_member_aircraft_qualification',
    Base.metadata,
    Column('crew_member_id', ForeignKey('crew_members.id')),
    Column('aircraft_id', ForeignKey('aircrafts.id'))
)
