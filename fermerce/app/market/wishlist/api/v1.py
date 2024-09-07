import typing as t
import uuid
from esmerald import APIView, Inject, Injects, get, post, put, delete
from fastapi import APIRouter, Depends, Query, status

from fermerce.app.wishlist import schemas, services
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.app.user import dependency

router = APIRouter(prefix="/wishlist", tags=["wish list"])


class WishlistAPIView(APIView):
    path = "/wishlist"
    tags = ["wish list"]
    dependencies = {"user": Inject(dependency.require_user)}

    @post("", status_code=status.HTTP_201_CREATED)
    async def create_whish(
        payload: schemas.IWishListIn,
        user: User = Injects(),
    ):
        return await services.create(payload=payload, user=user)

    @get("/")
    async def get_wish_list(
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

    @router.put("/{wish_item_id}", status_code=status.HTTP_200_OK)
    async def update_wish(
        wish_item_id: uuid.UUID,
        payload: schemas.IWishListIn,
        user: User = Injects(),
    ):
        return await services.update(
            payload=payload,
            user=user,
            wish_item_id=wish_item_id,
        )

    @get("/{wish_item_id}", status_code=status.HTTP_200_OK)
    async def get_wish(
        wish_item_id: uuid.UUID,
        user: User = Injects(),
        load_related: bool = False,
    ):
        return await services.get(
            wish_item_id=wish_item_id,
            user=user,
            load_related=load_related,
        )

    @delete("/{wish_item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_wish(
        wish_item_id: uuid.UUID,
        user: User = Injects(),
    ):
        return await services.delete(wish_item_id, user)
