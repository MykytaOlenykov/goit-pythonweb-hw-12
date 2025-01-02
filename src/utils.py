from fastapi import HTTPException, status
from pydantic import BaseModel


class HTTPBadRequestException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Bad request",
        )


class HTTPNotFoundException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Not found",
        )


class BadRequestModel(BaseModel):
    detail: str
    status_code: int = 400


class NotFoundModel(BaseModel):
    detail: str
    status_code: int = 404


bad_request_response_docs = {
    400: {
        "model": BadRequestModel,
        "description": "Bad request",
    },
}

not_found_response_docs = {
    404: {
        "model": NotFoundModel,
        "description": "Not found",
    },
}
