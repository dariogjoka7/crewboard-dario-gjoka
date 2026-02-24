import csv
import os
from datetime import datetime, timezone
from pathlib import Path
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect

from backend.db.models.aircraft import Aircraft
from backend.db.models.airport import Airport
from backend.db.models.crew_member import CrewMember
from backend.db.models.flight import Flight
from backend.db.models.user import User
from backend.auth.security import pwd_context

POSTGRES_URL = os.getenv("POSTGRES_URL")
engine = create_async_engine(POSTGRES_URL, echo=False) if POSTGRES_URL else None
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

CREW_MEMBERS_CSV_FILE_PATH = Path(__file__).parent / "seed_data/crew_member.csv"
FLIGHTS_CSV_FILE_PATH = Path(__file__).parent / "seed_data/flights.csv"


def parse_datetime(dt_str) -> datetime:
    current_year = datetime.now(timezone.utc).year
    dt = datetime.strptime(dt_str, "%b %d, %H:%M")
    return dt.replace(year=current_year, tzinfo=timezone.utc)


async def truncate_all_tables():
    async with engine.connect() as conn:
        # run_sync wraps sync code (like inspect)
        def _truncate(connection):
            inspector = inspect(connection)
            table_names = [t for t in inspector.get_table_names() if t != "alembic_version"]

            # defer constraints to avoid FK issues
            connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))

            for table in table_names:
                connection.execute(text(f"TRUNCATE TABLE {table} CASCADE"))

        await conn.run_sync(_truncate)
        await conn.commit()


async def seed():
    existing_aircrafts = {}
    existing_airports = {}

    async with async_session() as session:
        session.add(
            User(
                email='admin@email.com',
                password=pwd_context.hash('test')
            )
        )
        await session.commit()

    # Seed crew members
    async with async_session() as session:
        with open(CREW_MEMBERS_CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                aircrafts = []
                for aircraft_qual in row["Qualifications"].split(","):
                    aircraft = existing_aircrafts.setdefault(
                        aircraft_qual, Aircraft(type=aircraft_qual)
                    )
                    aircrafts.append(aircraft)

                airport = existing_airports.setdefault(row["Base"], Airport(code=row["Base"]))
                first_name, last_name = row["Name"].split(" ")

                crew_member = CrewMember(
                    employee_number=row["Emp"],
                    first_name=first_name,
                    last_name=last_name,
                    email=row["Email"],
                    aircraft_qualifications=aircrafts,
                    base_airport=airport,
                )

                session.add(crew_member)

        await session.commit()

    # Seed flights
    async with async_session() as session:
        with open(FLIGHTS_CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                aircraft = existing_aircrafts.get(row["Aircraft"])
                departure_airport = existing_airports.get(row["From"])
                arrival_airport = existing_airports.get(row["To"])

                flight = Flight(
                    number=row["ID"],
                    departure_airport=departure_airport,
                    arrival_airport=arrival_airport,
                    aircraft=aircraft,
                    scheduled_departure=parse_datetime(row["Departure"]),
                    scheduled_arrival=parse_datetime(row["Arrival"]),
                )

                session.add(flight)

        await session.commit()


async def main():
    await truncate_all_tables()
    await seed()

if __name__ == "__main__":
    asyncio.run(main())