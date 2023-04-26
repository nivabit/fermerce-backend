import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.products.category import schemas, services
from fermerce.core.enum.sort_type import SortOrder

# from fermerce.app.users.staff.dependency import require_super_admin_or_admin


router = APIRouter(prefix="/categories", tags=["Product Category"])


@router.post(
    "/",
    response_model=schemas.IProductCategoryOut,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def create_product_category(
    data_in: schemas.IProductCategoryIn,
) -> schemas.IProductCategoryOut:
    return await services.create(data_in=data_in)


@router.get(
    "/",
    response_model=schemas.IProductCategoryOutList
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_product_category_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    select: t.Optional[str] = Query(
        default="",
        alias="select",
        description="specific attributes of the categories",
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
):
    return await services.filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
    )


@router.get(
    "/{product_category_id}",
    response_model=schemas.IProductCategoryOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_product_category(
    product_category_id: uuid.UUID,
) -> schemas.IProductCategoryOut:
    return await services.get(product_category_id=product_category_id)


@router.put(
    "/{product_category_id}",
    response_model=schemas.IProductCategoryOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def update_product_category(
    product_category_id: uuid.UUID, permission: schemas.IProductCategoryIn
) -> schemas.IProductCategoryOut:
    return await services.update(
        product_category_id=product_category_id, data_in=permission
    )


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_total_product_category() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.delete(
    "/{product_category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def delete_product_category(product_category_id: uuid.UUID) -> None:
    return await services.delete(product_category_id=product_category_id)
