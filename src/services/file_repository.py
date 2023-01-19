from pathlib import Path
from typing import Generic, Type, Union

from fastapi import File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (FileNotCreatedError, FileNotFoundInStorageError,
                             InputTypeNotSupportedError)
from core.logger import logger
from models.orm_models import UserModel
from services.user_repository import CreateSchemaType, ModelType
from utils.files_utils import get_file_by_path, get_path_to_subfolder, write_file, zip_directory


class RepositoryDBFile(Generic[ModelType, CreateSchemaType]):

    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def get(self, db: AsyncSession, user: UserModel) -> list:
        statement = (select(self._model).where(self._model.author == user.id))
        result = await db.scalars(statement=statement)

        return result.all()

    async def download_file(self, db: AsyncSession, user: UserModel, path_or_id: Union[str, int]):
        try:
            id_ = int(path_or_id)
        except ValueError:
            id_ = path_or_id

        if isinstance(id_, int):
            return await self._get_file_by_id(db=db, user=user, id_=id_)
        elif isinstance(id_, str):
            return await get_file_by_path(user.id, user.name, id_)    # type: ignore

        raise InputTypeNotSupportedError()

    async def download_folder(self, user: UserModel, subpath: str = '') -> StreamingResponse:
        full_path_ = get_path_to_subfolder(user.id, user.name, subpath)    # type: ignore
        file_list = [Path.joinpath(full_path_, file.name) for file in list(full_path_.iterdir())]
        return zip_directory(file_list)

    async def create(
            self,
            user: UserModel,
            db: AsyncSession,
            subpath: str = '',
            file: UploadFile = File(),
    ) -> dict:

        directory_path_ = get_path_to_subfolder(user.id, user.name, subpath)    # type: ignore
        if not directory_path_.exists():
            directory_path_.mkdir(parents=True, exist_ok=True)

        written_bytes = await write_file(path_dir=directory_path_, file=file)

        logger.info(f'Write bytes: {written_bytes}')
        if Path.exists(Path.joinpath(directory_path_, file.filename)):
            await self._create_db_record(
                db=db,
                user=user,
                subpath=subpath,
                filename=file.filename,
                size=written_bytes,
            )
            size_ = "{:.3f}".format(written_bytes / 1024)    # noqa Q000
            return {
                'status': f'Successfully uploaded {file.filename}',
                'size': f'{size_} kb',
            }
        raise FileNotCreatedError()

    async def _create_db_record(
        self,
        size: int,
        db: AsyncSession,
        user: UserModel,
        subpath: str,
        filename: str,
    ) -> ModelType:
        file_record = self._model(name=filename,
                                  subpath=subpath,
                                  size=size,
                                  is_downloadable=True,
                                  author=user.id)
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        return file_record

    async def _get_path_by_id(self, db: AsyncSession, user: ModelType, id_: int) -> Path:
        statement = select(self._model).where(self._model.id == id_)
        file_record_ = await db.scalar(statement=statement)
        return Path.joinpath(get_path_to_subfolder(user.id, user.name, file_record_.subpath),
                             file_record_.name)

    async def _get_file_by_id(self, db: AsyncSession, user: UserModel, id_: int) -> FileResponse:
        file_path_ = await self._get_path_by_id(db=db, id_=id_, user=user)
        if not file_path_.exists() or not file_path_.is_file():
            raise FileNotFoundInStorageError()

        return FileResponse(path=file_path_)
