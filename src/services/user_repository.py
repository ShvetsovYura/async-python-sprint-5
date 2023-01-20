import json
from typing import Generic, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import mem_cache
from db.db import Base
from utils.utils import convert_to_user_object, hash_password

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class DBUserRepository(Generic[ModelType, CreateSchemaType]):

    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def add(self, db: AsyncSession, input_object: CreateSchemaType) -> ModelType:
        input_object_data = jsonable_encoder(input_object)
        hashed_password = hash_password(input_object_data.pop('password'))
        input_object_data['hashed_password'] = hashed_password
        db_record = self._model(**input_object_data)
        db.add(db_record)

        await db.commit()
        await db.refresh(db_record)

        return db_record

    async def get_user_by_name(self, db: AsyncSession, name: str) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.name == name)
        user = await db.execute(statement)

        return user.scalar_one_or_none()

    async def get_user_by_token(self, token: str) -> Optional[ModelType]:
        cached_user = mem_cache.get(token)
        if cached_user:
            user_data_ = json.loads(cached_user)    # type: ignore
            return convert_to_user_object(user_data_.get('user'))    # type: ignore
