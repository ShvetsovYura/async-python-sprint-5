import asyncio
from typing import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app import app
from db.db import Base, engine

from .mocks import BASE_URL


@pytest.fixture(scope='session')
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop()    # .get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        yield client


async def create_test_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def pytest_sessionstart(session):
    asyncio.get_event_loop().run_until_complete(drop_test_tables())

    asyncio.get_event_loop().run_until_complete(create_test_tables())


def pytest_sessionfinish(session, exitstatus):
    pass


@pytest_asyncio.fixture(scope='session')
async def async_session() -> AsyncGenerator:

    create_session: Callable = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with create_session() as session_:    # type:ignore
        yield session_
