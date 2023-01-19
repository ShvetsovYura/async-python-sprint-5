from typing import Union

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi_pagination import Page, paginate
from fastapi_pagination.ext.sqlalchemy import AbstractPage  # type: ignore
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (FileNotCreatedError, FileNotFoundHttpError,
                             FileNotFoundInStorageError, InternalServerErrorHttpError,
                             UpladedFileExceedError)
from db.db import get_session
from models.orm_models import FileModel, UserModel
from schemas.files import FileInDB, UploadResponse
from services.files import files_crud
from services.users import get_current_user

router = APIRouter()


@router.get('/list', response_model=Page[FileInDB], description='Get user file list.')
async def get_files_list(
        db: AsyncSession = Depends(get_session),
        user: UserModel = Depends(get_current_user),
) -> AbstractPage:
    files: list[FileModel] = await files_crud.get(db=db, user=user)

    return paginate([FileInDB(**file.__dict__) for file in files])


@router.post('/upload',
             status_code=status.HTTP_201_CREATED,
             description='Upload user file.',
             response_model=UploadResponse,
             response_model_exclude_unset=True)
async def upload_file(
        subdir: str = '',
        file: UploadFile = File(),
        db: AsyncSession = Depends(get_session),
        user: UserModel = Depends(get_current_user),
) -> UploadResponse:
    try:
        file_upload: dict = await files_crud.create(db=db, file=file, user=user, subpath=subdir)
    except UpladedFileExceedError:
        raise FileNotFoundHttpError(detail='Превышен размер файла')
    except FileNotCreatedError:
        raise InternalServerErrorHttpError(detail='Не удалось создать файл')
    except SQLAlchemyError:
        raise InternalServerErrorHttpError(detail='Не удалось добавить запись о файле')

    return UploadResponse(**file_upload)


@router.get('/download', description='Download user file.', response_class=FileResponse)
async def download_file(
    *,
    db: AsyncSession = Depends(get_session),
    user: UserModel = Depends(get_current_user),
    path_or_id: Union[str, int],
    download_folder: bool = False,
) -> Union[StreamingResponse, FileResponse]:

    try:
        if download_folder:
            file_ = await files_crud.download_folder(user=user, subpath=str(path_or_id))
        else:
            file_ = await files_crud.download_file(db, user, path_or_id)
    except FileNotFoundInStorageError:
        raise FileNotFoundHttpError(detail='Item not found')

    return file_
