import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from fermerce.app.user.dependency import require_user
from fermerce.app.address import schemas, services
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder

router = APIRouter(prefix="/shipping_address", tags=[" Shipping Address"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_address(
    data_in: schemas.IAddressIn,
    user: User = Depends(require_user),
):
    return await services.user_create(
        data_in=data_in,
        user=user,
    )


@router.get(
    "/",
    response_model=schemas.IAddressListOut,
    status_code=status.HTTP_200_OK,
)
async def get_address_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all through attributes"
    ),
    user: User = Depends(require_user),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc,
        description="order by attribute, e.g. id",
    ),
    order_by: t.Optional[str] = Query(
        default="id",
        description="order by attribute, e.g. id",
    ),
    load_related: bool = False,
):
    return await services.user_filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        user=user,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )


@router.get(
    "/{address_id}",
    response_model=schemas.IAddressOut,
    status_code=status.HTTP_200_OK,
)
async def get_address(
    address_id: uuid.UUID,
    user: User = Depends(require_user),
    load_related: bool = False,
):
    return await services.user_get(
        address_id=address_id,
        user=user,
        load_related=load_related,
    )


@router.put(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
)
async def update_address(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    user: User = Depends(require_user),
):
    return await services.user_update(
        address_id=address_id,
        data_in=data_in,
        user=user,
    )


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: uuid.UUID,
    user: User = Depends(require_user),
) -> Response:
    return await services.user_delete(
        address_id=address_id,
        user=user,
    )
