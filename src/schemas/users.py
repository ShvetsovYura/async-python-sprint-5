from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field, validator

from schemas import ConfigORM


class BaseWithORM(ConfigORM):

    name: str


class UserCreate(BaseWithORM):
    password: str


class UserInDB(BaseWithORM):
    hashed_password: str


class UserBase(BaseWithORM):
    id: int    # noqa A0003


class CachedUser(UserBase):
    is_active: bool


class UserToken(BaseModel):

    class Config:
        allow_population_by_field_name = True

        @validator('token')
        def hexlify_token(cls, value):
            """ Конвертирует UUID в hex строку """
            return value.hex

    token: UUID4 = Field(..., alias='access_token')
    expires: datetime
    token_type: Optional[str] = 'bearer'
