from models.orm_models import FileModel
from schemas.files import FileCreate
from services.file_repository import RepositoryDBFile


class RepositoryFile(RepositoryDBFile[FileModel, FileCreate]):
    pass


files_crud = RepositoryFile(FileModel)
