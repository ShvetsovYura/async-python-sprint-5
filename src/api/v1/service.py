import logging
import time

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import mem_cache
from db.db import get_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/ping', description='Checks the availability of services.')
async def get_ping(db: AsyncSession = Depends(get_session)) -> dict:

    start_time_db: float = time.time()
    await db.scalar(select(1))

    ping_db_duration: float = time.time() - start_time_db

    start_time_cache: float = time.time()

    mem_cache.ping()

    ping_cache_duration = time.time() - start_time_cache

    return {
        'datebase': "{:.4f}".format(ping_db_duration),    # noqa Q000
        'redis': "{:.4f}".format(ping_cache_duration),    # noqa Q000
    }
