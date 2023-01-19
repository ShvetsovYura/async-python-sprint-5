from typing import Any

from fastapi import HTTPException, status


class UpladedFileExceedError(Exception):
    pass


class FileNotFoundInStorageError(Exception):
    pass


class FileNotCreatedError(Exception):
    pass


class InputTypeNotSupportedError(Exception):
    pass


class FileNotFoundHttpError(HTTPException):

    def __init__(self, detail: Any = None) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserNotFoundHttpError(FileNotFoundHttpError):
    pass


class InternalServerErrorHttpError(HTTPException):

    def __init__(self, detail: Any = None) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class BadRequestHttpError(HTTPException):

    def __init__(self, detail: Any = None) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnprocessableEntityHttpError(HTTPException):

    def __init__(self, detail: Any = None) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
