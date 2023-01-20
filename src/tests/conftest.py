import asyncio
from typing import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app import app
from db.db import Base, engine
from utils.utils import hash_password


@pytest.fixture(scope='session')
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url='http://127.0.0.1') as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clear_data():
    async with engine.begin() as conn:
        await conn.execute(text('truncate table users cascade'))

        hashed_password = hash_password('P@ssw0rd')

        await conn.execute(
            text(f"""
                insert into users(name,hashed_password, is_active) 
                values('test_user', '{hashed_password}', true)
                """))    # noqa W291


async def create_test_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


def pytest_sessionstart(session):
    asyncio.get_event_loop().run_until_complete(drop_test_data())
    asyncio.get_event_loop().run_until_complete(create_test_data())


@pytest_asyncio.fixture(scope='session')
async def async_session() -> AsyncGenerator:

    create_session: Callable = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with create_session() as session_:    # type:ignore
        yield session_
