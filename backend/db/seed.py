import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from backend.db.models.aircraft import Aircraft
from backend.db.models.airport import Airport
from backend.db.models.crew_member import CrewMember
from backend.db.models.flight import Flight


POSTGRES_URL = os.getenv('POSTGRES_URL')
engine = create_engine(POSTGRES_URL) if POSTGRES_URL else None

CREW_MEMBERS_CSV_FILE_PATH = Path.home() / "Documents/personal/crewboard-dario-gjoka/backend/db/seed_data/crew_member.csv"
FLIGHTS_CSV_FILE_PATH = Path.home() / "Documents/personal/crewboard-dario-gjoka/backend/db/seed_data/flights.csv"


def parse_datetime(dt_str) -> datetime:
    current_year = datetime.now(timezone.utc).year
    dt = datetime.strptime(dt_str, "%b %d, %H:%M")
    dt = dt.replace(year=current_year, tzinfo=timezone.utc)
    return dt


def seed():
    existing_aircrafts = {}
    existing_airports = {}

    with open(CREW_MEMBERS_CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        with Session(engine) as session:
            for row in reader:
                aircrafts = []
                for aircraft_qual in row['Qualifications'].split(","):
                    aircraft = existing_aircrafts.setdefault(aircraft_qual, Aircraft(type=aircraft_qual))
                    aircrafts.append(aircraft)

                airport = existing_airports.setdefault(row['Base'], Airport(code=row['Base']))
                first_name, last_name = row['Name'].split(' ')

                crew_member = CrewMember(
                    employee_number=row['Emp'],
                    first_name=first_name,
                    last_name=last_name,
                    email=row['Email'],
                    aircraft_qualifications=aircrafts,
                    base_airport=airport
                )

                session.add(crew_member)
                session.flush()
                session.commit()

    with open(FLIGHTS_CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        with Session(engine) as session:
            for row in reader:
                aircraft = existing_aircrafts.get(row['Aircraft'])
                departure_airport = existing_airports.get(row['From'])
                arrival_airport = existing_airports.get(row['To'])

                flight = Flight(
                    number=row["ID"],
                    departure_airport=departure_airport,
                    arrival_airport=arrival_airport,
                    aircraft=aircraft,
                    scheduled_departure=parse_datetime(row["Departure"]),
                    scheduled_arrival=parse_datetime(row["Arrival"])
                )

                session.add(flight)
                session.flush()
                session.commit()


def truncate_all_tables():
    with Session(engine) as session:
        inspector = inspect(engine)
        table_names = [n for n in inspector.get_table_names() if n != "alembic_version"]
        session.execute(text("SET CONSTRAINTS ALL DEFERRED"))

        for table in table_names:
            session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))

        session.commit()


if __name__ == "__main__":
    truncate_all_tables()
    seed()
