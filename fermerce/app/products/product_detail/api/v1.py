import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.users.user.models import User
from fermerce.app.products.product_detail import schemas, services
from fermerce.core.enum.sort_type import SortOrder
from fermerce.app.users.user import dependency


router = APIRouter(prefix="/product_details", tags=["Product details"])


@router.get("/")
async def get_product_detail_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter through all attributes"
    ),
    product_id: t.Optional[str] = Query(
        default="", description="filter through a specific product"
    ),
    select: t.Optional[str] = Query(
        default="", alias="select", description="select specific attributes"
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
    load_related: t.Optional[bool] = False,
):
    return await services.filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        product_id=product_id,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product_details(
    data_in: schemas.IProductDetailsIn,
    user: User = Depends(dependency.require_vendor),
):
    return await services.create_details(data_in=data_in, user=user)


@router.get("/{detail_id}", response_model=schemas.IProductDetailsOut)
async def get_product_detail(
    detail_id: uuid.UUID,
) -> schemas.IProductDetailsOut:
    return await services.get_detail(detail_id=detail_id)


@router.put("/", response_model=schemas.IProductDetailsOut)
async def update_product_detail(
    data_in: schemas.IProductDetailsUpdateIn,
    user: User = Depends(dependency.require_vendor),
) -> schemas.IProductDetailsOut:
    return await services.update_product_detail(user=user, data_in=data_in)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    data_in: schemas.IProductDetailsRemoveIn,
    user: User = Depends(dependency.require_vendor),
) -> None:
    return await services.delete_product_detail(data_in=data_in, user=user)
