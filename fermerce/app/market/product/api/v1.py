import typing as t
import uuid
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status
from fermerce.app.vendor.models import Vendor
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.product import schemas, services
from fermerce.core.enum.sort_type import SearchType, SortOrder
from fermerce.app.staff.dependency import require_super_admin_or_admin
from fermerce.app.vendor import dependency


router = APIRouter(prefix="/products", tags=["Product"])


@router.post("/")
async def create_product(
    data_in: schemas.IProductIn,
    vendor: Vendor = Depends(dependency.require_vendor),
):
    return await services.create(
        vendor,
        data_in,
    )


@router.get("/", response_model=schemas.IProductListOut)
async def get_products_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter through all attributes"
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
    is_suspended: t.Optional[bool] = False,
    in_stock: t.Optional[bool] = False,
    search_type: t.Optional[SearchType] = SearchType._and,
    load_related: t.Optional[bool] = False,
):
    return await services.filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
        is_suspended=is_suspended,
        in_stock=in_stock,
        search_type=search_type,
        load_related=load_related,
    )


@router.get("/{slug}", response_model=schemas.IProductOut)
async def get_product(slug: str, load_related: bool = False):
    return await services.get(slug=slug, load_related=load_related)


@router.put("/{product_id}", response_model=schemas.IProductOut)
async def update_product(
    product_id: uuid.UUID,
    request: Request,
    data_in: schemas.IProductIn,
    vendor: Vendor = Depends(dependency.require_vendor),
) -> schemas.IProductListOut:
    return await services.update(
        vendor=vendor, product_id=product_id, data_in=data_in, request=request
    )


@router.get(
    "/total/count",
    response_model=ITotalCount,
)
async def get_total_product() -> t.Optional[ITotalCount]:
    return await services.get_product_count()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    vendor: Vendor = Depends(dependency.require_vendor),
) -> None:
    return await services.delete(product_id=product_id, vendor=vendor)
