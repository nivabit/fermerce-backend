import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.business.vendor.models import Vendor
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage, ITotalCount
from fermerce.app.products.promo_code import schemas, services
from fermerce.app.business.vendor.dependency import require_vendor


router = APIRouter(prefix="/promocodes", tags=["Product Promo Codes"])


@router.post(
    "/",
    response_model=schemas.IProductPromoCodeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_promo_code(
    data_in: schemas.IProductPromoCodeIn, vendor: Vendor = Depends(require_vendor)
) -> schemas.IProductPromoCodeOut:
    return await services.create(data_in=data_in, vendor=vendor)


@router.get("/", response_model=schemas.IProductPromoCodeListOut)
async def get_promo_code_list(
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
        sort_by=sort_by,
        order_by=order_by,
        select=select,
    )


@router.get("/{promo_code_id}", response_model=schemas.IProductPromoCodeOut)
async def get_promo_code(
    promo_code_id: uuid.UUID, vendor: Vendor = Depends(require_vendor)
) -> schemas.IProductPromoCodeOut:
    return await services.get(promo_code_id=promo_code_id, vendor=vendor)


@router.put("/{promo_code_id}", response_model=schemas.IProductPromoCodeOut)
async def update_promo_code(
    promo_code_id: uuid.UUID,
    data_in: schemas.IProductPromoCodeIn,
    vendor: Vendor = Depends(require_vendor),
) -> schemas.IProductPromoCodeOut:
    return await services.update(
        promo_code_id=promo_code_id, data_in=data_in, vendor=vendor
    )


@router.get("/total/count", response_model=ITotalCount)
async def get_total_promo_code(
    vendor: Vendor = Depends(require_vendor),
) -> t.Optional[ITotalCount]:
    return await services.get_total_count(vendor)


@router.post("/products", status_code=status.HTTP_200_OK)
async def add_product_to_promo_code(
    data_in: schemas.IProductPromoCodeUpdateIn,
    vendor: Vendor = Depends(require_vendor),
) -> IResponseMessage:
    return await services.add_product_to_promo_code(data_in=data_in, vendor=vendor)


@router.delete("/products", status_code=status.HTTP_200_OK)
async def remove_product_from_promo_code(
    data_in: schemas.IProductPromoCodeRemoveIn,
    vendor: Vendor = Depends(require_vendor),
) -> IResponseMessage:
    return await services.delete_product_from_promo_code(data_in=data_in, vendor=vendor)


@router.delete("/{promo_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promo_code(
    promo_code_id: uuid.UUID, vendor: Vendor = Depends(require_vendor)
) -> None:
    return await services.delete(promo_code_id=promo_code_id, vendor=vendor)
