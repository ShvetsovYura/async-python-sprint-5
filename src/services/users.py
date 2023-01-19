from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.orm_models import UserModel
from schemas.users import UserCreate
from services.user_repository import DBUserRepository


class RepositoryUser(DBUserRepository[UserModel, UserCreate]):
    pass


user_crud = RepositoryUser(UserModel)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v1/auth')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await user_crud.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return user
