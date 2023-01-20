import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings, mem_cache
from core.exceptions import (BadRequestHttpError, UnprocessableEntityHttpError,
                             UserNotFoundHttpError)
from db.db import get_session
from schemas import users as schema
from services.users import get_current_user, user_crud
from utils.utils import convert_to_user_dict, validate_password

router = APIRouter()


@router.post('/signup',
             description='New user registration.',
             status_code=status.HTTP_201_CREATED,
             response_model=schema.UserBase)
async def signup(
        user: schema.UserCreate,
        db: AsyncSession = Depends(get_session),
) -> schema.UserBase:
    try:
        new_user_ = await user_crud.add(db, user)
    except IntegrityError:
        raise BadRequestHttpError(detail='Select another name')
    except SQLAlchemyError:
        raise UnprocessableEntityHttpError()

    return schema.UserBase(**new_user_.__dict__)


@router.post('/singin',
             description='Chek username/password and get token.',
             status_code=status.HTTP_202_ACCEPTED,
             response_model=schema.UserToken)
async def signin(form_data: OAuth2PasswordRequestForm = Depends(),
                 db: AsyncSession = Depends(get_session)) -> schema.UserToken:
    user = await user_crud.get_user_by_name(db=db, name=form_data.username)
    if not user:
        raise UserNotFoundHttpError(detail='User not found')
    if not validate_password(form_data.password, user.hashed_password):    # type: ignore
        raise BadRequestHttpError(detail='Incorrect name or password')

    expires_ = +timedelta(minutes=app_settings.access_token_expire_minutes)
    expires_at_ = (datetime.now() + expires_)
    token_ = uuid.uuid4()
    mem_cache.set(str(token_),
                  json.dumps({
                      'expires': expires_at_.timestamp(),
                      'user': convert_to_user_dict(user),
                  }),
                  ex=expires_)
    return schema.UserToken(access_token=token_, expires=expires_at_)


@router.get('/me', response_model=schema.UserBase, description='Get current user name and id')
async def who_i_am(current_user=Depends(get_current_user)) -> schema.UserBase:
    return schema.UserBase(id=current_user.id, name=current_user.name)
