import uuid
from fastapi import APIRouter, Depends, status
from fermerce.app.markets.tracking import services, schemas
from fermerce.app.users.staff.dependency import require_dispatcher

router = APIRouter(prefix="/trackings", tags=["Tracking"])


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_dispatcher)])
async def create_tracking(data_in: schemas.ITrackIn):
    return await services.create(data_in=data_in)


@router.put(
    "/{track_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_dispatcher)],
)
async def update_tracking(track_id: uuid.UUID, data_in: schemas.ITrackIn):
    return await services.update(track_id=track_id, data_in=data_in)


@router.get(
    "/{track_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_dispatcher)],
)
async def create_tracking(track_id: uuid.UUID):
    return await services.get(track_id)


@router.get(
    "/items/{order_items_id}/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_dispatcher)],
)
async def get_trackings(order_item_id: uuid.UUID):
    return await services.filter(order_item_id=order_item_id)


@router.delete(
    "/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_dispatcher)],
)
async def delete_tracking(track_id: uuid.UUID) -> None:
    return await services.delete(track_id=track_id)
