import os
import sys

import redis
from pydantic import BaseSettings


class AppSettings(BaseSettings):

    class Config:
        env_file = '.env'

    app_title: str = 'FastApi File Server'
    db_user: str = 'app'
    db_password: str = '123qwe'
    db_name: str = 'cutter_db'
    db_host: str = 'postgres'
    db_port: int = 5432

    cache_host = 'memcache'
    test_cache_host = '127.0.0.1'
    cache_port = 6379

    project_host: str = '0.0.0.0'
    project_port: int = 8000
    db_dsn: str = (f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    algorithm: str = 'sha256'
    hmac_iteration = 10_000
    access_token_expire_minutes = 300
    file_folder = 'files_storage'

    test_db_name = 'cutter_db_test'
    test_db_pwd = '123qwe'

    test_db_dsn: str = (
        f'postgresql+asyncpg://{db_user}:{test_db_pwd}@localhost:{db_port}/{test_db_name}')

    secret_key: str = ('09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7')


app_settings = AppSettings()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mem_cache = redis.Redis(host=app_settings.cache_host, port=app_settings.cache_port)

if 'pytest' in sys.modules:
    mem_cache = redis.Redis(host=app_settings.test_cache_host, port=app_settings.cache_port)
