from fastapi import HTTPException, status
from pydantic import BaseModel


class HTTPBadRequestException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Bad request",
        )


class BadRequestModel(BaseModel):
    detail: str
    status_code: int = 400


bad_request_response_docs = {
    400: {
        "model": BadRequestModel,
        "description": "Bad request",
    },
}


class HTTPUnauthorizedException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or "Unauthorized",
        )


class UnauthorizedModel(BaseModel):
    detail: str
    status_code: int = 401


unauthorized_response_docs = {
    401: {
        "model": UnauthorizedModel,
        "description": "Unauthorized",
    },
}


class HTTPNotFoundException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Not found",
        )


class NotFoundModel(BaseModel):
    detail: str
    status_code: int = 404


not_found_response_docs = {
    404: {
        "model": NotFoundModel,
        "description": "Not found",
    },
}


class HTTPConflictException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail or "Not found",
        )


class ConflictModel(BaseModel):
    detail: str
    status_code: int = 409


conflict_response_docs = {
    409: {
        "model": ConflictModel,
        "description": "Conflict",
    },
}
