import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status

from fermerce.app.cart import schemas, services
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.app.user import dependency

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_cart(
    data_in: schemas.ICartIn, user: User = Depends(dependency.require_user)
):
    return await services.create(data_in=data_in, user=user)


@router.put("/{cart_id}", status_code=status.HTTP_200_OK)
async def update_cart(
    cart_id: uuid.UUID,
    data_in: schemas.ICartIn,
    user: User = Depends(dependency.require_user),
):
    return await services.update(data_in=data_in, user=user, cart_id=cart_id)


@router.get("/")
async def get_carts(
    filter_string: str = Query(
        default=None, description="filter through product on the category"
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc,
        description="order by attribute, e.g. ascending, descending",
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id, created_at"
    ),
    select: t.Optional[str] = Query(
        default="", description="order by attribute, e.g. id, created_at"
    ),
    load_related: bool = False,
    user: User = Depends(dependency.require_user),
):
    return await services.filter(
        user=user,
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
        select=select,
    )


@router.get("/{cart_id}", status_code=status.HTTP_200_OK)
async def get_cart(cart_id: uuid.UUID, user: User = Depends(dependency.require_user)):
    return await services.get(cart_id, user.id)


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    cart_id: uuid.UUID, user: User = Depends(dependency.require_user)
):
    return await services.delete(cart_id, user)
