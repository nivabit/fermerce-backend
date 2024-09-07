from enum import Enum
from typing import Any
from esmerald import HTTPException, status
from pydantic import BaseModel


class SortEnum(Enum):
    ASC = "asc"
    DESC = "desc"


class IHealthCheck(BaseModel):
    name: str
    version: float
    description: str
    docs_url: str
    redoc_url: str


class IResponseMessage(BaseModel):
    data: Any
    status_code: int = 200


def get_response(
    data: Any,
    status_code: int = 200,
):
    data_map = {}
    if isinstance(data, BaseModel):
        data_map = data.model_dump()
    data_map = data

    return IResponseMessage(
        data=data_map,
        status_code=status_code,
    )


def get_error_response(
    detail: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> HTTPException:
    return HTTPException(
        detail=dict(
            message=detail,
            status_code=status_code,
        ),
        status_code=status_code,
    )


class IFilterList(BaseModel):
    previous: int | None = None
    next: int | None = None
    total_count: int = 0
    data: list[Any] = []

    class Config:
        from_attributes = True


class IFilterSingle(BaseModel):
    data: Any
    status: int

    class Config:
        from_attributes = True


class ICount(BaseModel):
    count: int = 0


class IError(BaseModel):
    detail: str
    status_code: int = 401
