import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from fermerce.app.business.address.enum import SaveTypeEnum
from fermerce.app.users.user.dependency import require_user
from fermerce.app.business.address import schemas, services
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder

router = APIRouter(prefix="/address", tags=["Address"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.IAddressOut,
)
async def create_address(
    data_in: schemas.IAddressIn,
    user: User = Depends(require_user),
    user_type: SaveTypeEnum = SaveTypeEnum.customer,
):
    return await services.create(data_in=data_in, user=user, user_type=user_type)


@router.get(
    "/",
    response_model=schemas.IAddressListOut,
    status_code=status.HTTP_200_OK,
)
async def get_address_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all through attributes"
    ),
    user_type: SaveTypeEnum = SaveTypeEnum.customer,
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
    return await services.filter(
        filter_string=filter_string,
        get_type=user_type,
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
    user_type: SaveTypeEnum = SaveTypeEnum.customer,
):
    return await services.get(
        address_id=address_id,
        user=user,
        load_related=load_related,
        get_type=user_type,
    )


@router.put(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.IAddressOut,
)
async def update_address(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    user: User = Depends(require_user),
    save_type: SaveTypeEnum = SaveTypeEnum.customer,
):
    return await services.update(
        address_id=address_id,
        data_in=data_in,
        user=user,
        save_type=save_type,
    )


@router.get("/total/count", response_model=dict)
async def get_total_address(
    user: User = Depends(require_user),
) -> t.Optional[int]:
    return await services.get_total_count(user)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: uuid.UUID,
    user: User = Depends(require_user),
    save_type: SaveTypeEnum = SaveTypeEnum.customer,
) -> Response:
    return await services.delete(
        address_id=address_id,
        user=user,
        delete_type=save_type,
    )
