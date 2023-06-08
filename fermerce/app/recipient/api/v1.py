import uuid
from fastapi import APIRouter, Depends, status
from fermerce.app.recipient import services, schemas
from fermerce.app.vendor import dependency
from fermerce.app.vendor.models import Vendor
from fermerce.core.schemas.response import IResponseMessage


router = APIRouter(
    prefix="/bank_details",
    tags=["Vendor business bank account"],
)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=IResponseMessage,
)
async def add_bank_detail(
    data_in: schemas.IBankIn,
    vendor: Vendor = Depends(dependency.require_vendor),
):
    return await services.add_vendor_bank(
        data_in=data_in,
        vendor=vendor,
    )


@router.get("/{bank_detail_id}", status_code=status.HTTP_200_OK)
async def get_single_detail(
    bank_detail_id: uuid.UUID,
    load_related: bool = False,
    vendor: Vendor = Depends(dependency.require_vendor),
):
    return await services.get_single_bank_detail(
        bank_detail_id=bank_detail_id,
        load_related=load_related,
        vendor=vendor,
    )


@router.put("/{bank_detail_id}", status_code=status.HTTP_200_OK)
async def update_single_detail(
    bank_detail_id: uuid.UUID,
    data_in: schemas.IBankUpdateIn,
    vendor: Vendor = Depends(dependency.require_vendor),
):
    return await services.update_vendor_bank(
        bank_detail_id=bank_detail_id,
        vendor=vendor,
        data_in=data_in,
    )
