from contextlib import asynccontextmanager
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session


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
