import typing as t
import uuid
from fastapi import APIRouter, Response, status
from fermerce.app.markets.status import schemas, services
from fermerce.core.schemas.response import ITotalCount


router = APIRouter(prefix="/status", tags=["Status"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_status(data_in: schemas.IStatusIn) -> schemas.IStatusOut:
    return await services.create(data_in=data_in)


@router.get(
    "/{status_id}",
    response_model=schemas.IStatusOut,
    status_code=status.HTTP_200_OK,
)
async def get_status(status_id: uuid.UUID) -> schemas.IStatusOut:
    return await services.get(status_id=status_id)


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_total_state() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.put(
    "/{status_id}",
    response_model=schemas.IStatusOut,
    status_code=status.HTTP_200_OK,
)
async def update_status(status_id: uuid.UUID, data_in: schemas.IStatusIn):
    return await services.update(status_id=status_id, data_in=data_in)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status(status_id: uuid.UUID) -> Response:
    return await services.delete(status_id=status_id)
