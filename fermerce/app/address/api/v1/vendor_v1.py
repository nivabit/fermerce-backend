import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from fermerce.app.vendor.dependency import require_vendor
from fermerce.app.address import schemas, services
from fermerce.app.vendor.models import Vendor
from fermerce.core.enum.sort_type import SortOrder

router = APIRouter(prefix="/business_address", tags=[" Business Address"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.IAddressOut,
)
async def create_address(
    data_in: schemas.IAddressIn,
    vendor: Vendor = Depends(require_vendor),
):
    return await services.vendor_create(
        data_in=data_in,
        vendor=vendor,
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
    vendor: Vendor = Depends(require_vendor),
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
    return await services.vendor_filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        vendor=vendor,
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
    vendor: Vendor = Depends(require_vendor),
    load_related: bool = False,
):
    return await services.vendor_get(
        address_id=address_id,
        vendor=vendor,
        load_related=load_related,
    )


@router.put(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.IAddressOut,
)
async def update_address(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    vendor: Vendor = Depends(require_vendor),
):
    return await services.update(
        address_id=address_id,
        data_in=data_in,
        vendor=vendor,
    )


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: uuid.UUID,
    vendor: Vendor = Depends(require_vendor),
) -> Response:
    return await services.vendor_delete(
        address_id=address_id,
        vendor=vendor,
    )
