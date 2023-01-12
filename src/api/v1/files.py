import time
from typing import Union

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from fastapi_pagination import Page, paginate
from fastapi_pagination.ext.sqlalchemy import AbstractPage  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import re_cli
from db.db import get_session
from models.users import UsersTable as User
from schemas.files import FileInDB, UploadResponse
from services.files import files_crud
from services.users import get_current_user

router = APIRouter()


@router.get('/ping', description='Checks the availability of services.')
async def get_ping(
        db: AsyncSession = Depends(get_session),    # noqa B008
        user: User = Depends(get_current_user),    # noqa B008
) -> dict:
    start_time = time.time()
    await files_crud.get(db=db, user=user)
    ping_db = time.time() - start_time
    start_time = time.time()
    re_cli.get('nothing')
    ping_redis = time.time() - start_time
    return {
        'datebase': "{:.4f}".format(ping_db),    # noqa Q000
        'redis': "{:.4f}".format(ping_redis),    # noqa Q000
        'user': {
            'name': user.name,
            'id': user.id,
        },
    }


@router.get('/list', response_model=Page[FileInDB], description='Get user file list.')
async def get_files_list(
        db: AsyncSession = Depends(get_session),    # noqa B008
        user: User = Depends(get_current_user),    # noqa B008
) -> AbstractPage:
    files = await files_crud.get(db=db, user=user)
    return paginate(files)


@router.post('/upload',
             status_code=status.HTTP_201_CREATED,
             description='Upload user file.',
             response_model=UploadResponse,
             response_model_exclude_unset=True)
async def upload_file(
        path: str,
        db: AsyncSession = Depends(get_session),    # noqa B008
        user: User = Depends(get_current_user),    # noqa B008
        file: UploadFile = File(),    # noqa B008
) -> UploadResponse:
    file_upload = await files_crud.create(db=db, file=file, user=user, path=path)
    return UploadResponse(**file_upload)


@router.get('/download', description='Download user file.', response_class=FileResponse)
async def download_file(
    *,
    db: AsyncSession = Depends(get_session),    # noqa B008
    user: User = Depends(get_current_user),    # noqa B008
    identifier: Union[str, int, None] = None,
    download_folder: bool = False,
) -> FileResponse:
    if download_folder:
        file = await files_crud.download_folder(user=user, path=identifier)
    else:
        file = await files_crud.download_file(db=db, user=user, identifier=identifier)
    return file
