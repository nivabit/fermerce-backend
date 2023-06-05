import uuid
import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.tracking import services, schemas
from fermerce.app.staff.dependency import require_dispatcher

router = APIRouter(prefix="/trackings", tags=["Tracking"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    #  dependencies=[Depends(require_dispatcher)]
)
async def create_tracking(data_in: schemas.ITrackIn):
    return await services.create(data_in=data_in)


@router.put(
    "/{track_id}",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_dispatcher)],
)
async def update_tracking(track_id: uuid.UUID, data_in: schemas.ITrackIn):
    return await services.update(track_id=track_id, data_in=data_in)


@router.get(
    "/{track_id}",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_dispatcher)],
)
async def create_tracking(track_id: uuid.UUID, load_related: bool = False):
    return await services.get(track_id=track_id, load_related=load_related)


@router.get(
    "/items/{order_item_id}/",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_dispatcher)],
)
async def get_trackings(
    order_item_id: str,
    per_page: int = 10,
    page: int = 1,
    select: t.Optional[str] = Query(
        default="", description="select order direct attributes, e.g. id"
    ),
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    load_related: bool = False,
):
    return await services.filter(
        order_item_id=order_item_id,
        per_page=per_page,
        page=page,
        select=select,
        load_related=load_related,
        filter_string=filter_string,
    )


@router.delete(
    "/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_dispatcher)],
)
async def delete_tracking(track_id: uuid.UUID) -> None:
    return await services.delete(track_id=track_id)
