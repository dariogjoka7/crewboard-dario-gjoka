from sqlalchemy import Table, Column, ForeignKey

from backend.db.models.base import Base

crew_member_flight_assignment_assoc_table = Table(
    'crew_member_flight_assignments',
    Base.metadata,
    Column('crew_member_id', ForeignKey('crew_members.id')),
    Column('flight_id', ForeignKey('flights.id')),
    extend_existing=True
)
