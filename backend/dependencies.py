from typing import Annotated
from contextlib import asynccontextmanager, contextmanager
import os

from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from backend.db.models import CrewMember, Aircraft
from backend.db.repos.aircraft_repo import AircraftRepo
from backend.db.repos.airport_repo import AirportRepo
from backend.db.repos.crew_member_repo import CrewMemberRepo
from backend.db.repos.flight_repo import FlightRepo
from backend.routers.models.assignment.assignment_create import AssignmentCreate
from backend.services.assignment_service import AssignmentService
from backend.services.crew_member_service import CrewMemberService
from backend.services.flight_service import FlightService


def create_session(is_async: bool = False) -> AsyncSession | Session:
    try:
        postgres_url = os.getenv('POSTGRES_URL')
        url = postgres_url.replace('postgresql://', 'postgresql+asyncpg://') if is_async else postgres_url
        engine = create_async_engine(url) if is_async else create_engine(url)
        maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) if is_async \
            else sessionmaker(bind=engine)
        return maker()
    except Exception as e:
        print('Could not create a connection with the database. POSTGRES_URL is missing.')
        raise e


@contextmanager
def get_session():
    session = create_session()

    try:
        yield session
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()


@asynccontextmanager
async def get_session_async():
    session = create_session(is_async=True)

    try:
        yield session
    finally:
        await session.close()


async def get_session_dep():
    async with get_session_async() as session:
        print("Successfully connected to the db session")
        yield session


def get_crew_member_service(session: Annotated[AsyncSession, Depends(get_session_dep)]) -> CrewMemberService:
    airport_repo = AirportRepo(session)
    aircraft_repo = AircraftRepo(session)
    crew_member_repo = CrewMemberRepo(session)

    return CrewMemberService(airport_repo, aircraft_repo, crew_member_repo)


def get_flight_service(session: Annotated[AsyncSession, Depends(get_session_dep)]) -> FlightService:
    airport_repo = AirportRepo(session)
    aircraft_repo = AircraftRepo(session)
    flight_repo = FlightRepo(session)

    return FlightService(airport_repo, aircraft_repo, flight_repo)


def get_assignment_service(session: Annotated[AsyncSession, Depends(get_session_dep)]) -> AssignmentService:
    crew_member_repo = CrewMemberRepo(session)
    flight_repo = FlightRepo(session)

    return AssignmentService(crew_member_repo, flight_repo)
