import sys
from datetime import timezone, datetime, timedelta
from pathlib import Path

from httpx import ASGITransport, AsyncClient

from backend.db.models import Airport, Aircraft
from backend.db.models import CrewMember
from backend.db.models import Flight

# Ensure project root is on sys.path so `import backend...` works during pytest collection
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from backend.db.models.base import Base
from backend.main import app


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest.fixture()
async def db_connection(engine):
    """Create a fresh connection and transaction for each test."""
    async with engine.connect() as conn:
        trans = await conn.begin()  # Start a transaction
        yield conn
        await trans.rollback()  # Roll back everything after test

@pytest.fixture()
async def db_session(db_connection):
    async_session = sessionmaker(bind=db_connection, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture()
async def test_app(db_session):
    from backend.dependencies import get_session_dep
    from backend.auth.dependencies import get_current_user
    from backend.db.models.user import User

    async def _get_session_override():
        yield db_session

    async def _get_current_user_override():
        return User(
            id=1,
            email="test@example.com",
            password="x",
        )

    app.dependency_overrides[get_session_dep] = _get_session_override
    app.dependency_overrides[get_current_user] = _get_current_user_override

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def crew_member_seeded_data(db_session):
    ap = Airport(code="FRA")
    a = Aircraft(type="A320")
    crew_member = CrewMember(employee_number='E100', first_name='Test', last_name='User', email='t@example.com')
    crew_member.base_airport = ap
    crew_member.aircraft_qualifications.append(a)

    db_session.add(crew_member)
    await db_session.flush()

    yield ap, a

@pytest.fixture
async def flights_data(db_session):
    ap = Airport(code='DDD')
    ap2 = Airport(code='EEE')
    a = Aircraft(type='B737')

    db_session.add_all([ap, ap2, a])
    await db_session.flush()

    return ap, ap2, a


@pytest.fixture
async def assignments_data(db_session):
    ap = Airport(id=1, code='ZZZ')
    a = Aircraft(id=1, type='AX1')
    db_session.merge(ap)
    db_session.merge(a)

    cm = CrewMember(employee_number='E200', first_name='Auto', last_name='Crew', email='auto@example.com', base_airport_id=ap.id)
    cm.base_airport = ap
    cm.aircraft_qualifications.append(a)
    db_session.add(cm)

    now = datetime.now(timezone.utc) + timedelta(days=1)
    f1 = Flight(number='A1', departure_airport_id=ap.id, arrival_airport_id=ap.id, aircraft_id=a.id,
                scheduled_departure=now, scheduled_arrival=now + timedelta(hours=2))
    f2 = Flight(number='A2', departure_airport_id=ap.id, arrival_airport_id=ap.id, aircraft_id=a.id,
                scheduled_departure=now + timedelta(hours=12), scheduled_arrival=now + timedelta(hours=14))

    db_session.add_all([f1, f2])
    await db_session.flush()

    return ap, a, cm, f1, f2


@pytest.fixture
async def assignment_data_second(db_session):
    a = Aircraft(id=1, type='A1')
    ap = Airport(id=1, code='AAA')
    db_session.add(ap)
    db_session.add(a)

    cm = CrewMember(employee_number='E100', first_name='T', last_name='User', email='t@example.com', base_airport_id=ap.id)
    cm.aircraft_qualifications.append(a)
    db_session.add(cm)

    dep1 = datetime.now(timezone.utc)
    arr1 = dep1 + timedelta(hours=2)
    dep2 = arr1 + timedelta(hours=5)  # only 5 hours rest
    arr2 = dep2 + timedelta(hours=2)

    f1 = Flight(number='F1', departure_airport_id=ap.id, arrival_airport_id=ap.id, aircraft_id=a.id, scheduled_departure=dep1,
                scheduled_arrival=arr1)
    f2 = Flight(number='F2', departure_airport_id=ap.id, arrival_airport_id=ap.id, aircraft_id=a.id, scheduled_departure=dep2,
                scheduled_arrival=arr2)
    db_session.add_all([f1, f2])

    # manually attach first flight to crew
    cm.flight_assignments.append(f1)

    await db_session.flush()

    yield cm, f2


@pytest.fixture
async def assignment_data_third(db_session):
    a1 = Aircraft(id=1, type='A1')
    a2 = Aircraft(id=2, type='A2')
    ap = Airport(id=3, code='BBB')
    db_session.add(ap)
    db_session.add(a1)
    db_session.add(a2)

    cm = CrewMember(employee_number='E101', first_name='Q', last_name='User', email='q@example.com', base_airport_id=ap.id)
    cm.aircraft_qualifications.append(a1)
    db_session.add(cm)

    dep = datetime.now(timezone.utc) + timedelta(days=1)
    arr = dep + timedelta(hours=2)
    f = Flight(number='FQ', departure_airport_id=ap.id, arrival_airport_id=ap.id, aircraft_id=a2.id, scheduled_departure=dep,
               scheduled_arrival=arr)
    db_session.add(f)

    cm.flight_assignments.append(f)

    await db_session.flush()

    yield cm, f
