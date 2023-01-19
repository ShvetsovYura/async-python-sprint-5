from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas import ConfigORM


class FileBase(BaseModel):
    name: str


class FileCreate(FileBase):
    pass


class FileUpload(BaseModel):
    path: str


class FileInDBBase(ConfigORM, FileBase):
    id: int    # noqa VNE0003
    created_at: datetime
    subpath: Optional[str]
    size: int
    is_downloadable: bool


class File(FileInDBBase):
    pass


class FileInDB(FileInDBBase):
    pass


class UploadResponse(BaseModel):
    status: Optional[str] = None
    size: Optional[str] = None
