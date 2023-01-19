import hashlib
import random
import string
from typing import Optional, Union

from core.config import app_settings
from models.orm_models import UserModel
from schemas.users import CachedUser


def get_random_string(length=12) -> str:
    """ Генерирует случайную строку. """

    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """ Хеширует пароль. """

    if salt is None:
        salt = get_random_string()
    enc: bytes = hashlib.pbkdf2_hmac(app_settings.algorithm, password.encode(), salt.encode(),
                                     app_settings.hmac_iteration)
    return f'{salt}${enc.hex()}'


def validate_password(password: str, hashed_password: str) -> bool:
    """ Проверяет, что хеш пароля совпадает с хешем из БД. """

    salt: str = hashed_password.split('$')[0]
    return hash_password(password, salt) == hashed_password


def convert_to_user_dict(user: Union[CachedUser, UserModel]) -> dict:
    return {
        'id': user.id,
        'name': user.name,
        'is_active': 1 if user.is_active else 0,
    }


def convert_to_user_object(user: dict) -> CachedUser:
    return CachedUser(name=user.get('name', 'unknown_name'),
                      id=user.get('id', -1),
                      is_active=True if user.get('is_active') else False)


def join_user(id_: int, name: str) -> str:
    return ''.join([str(id_), '_', name])
