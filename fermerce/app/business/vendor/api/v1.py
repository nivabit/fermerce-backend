import typing as t
import uuid
from fastapi import APIRouter, Depends, Request, status
from fermerce.app.business.vendor import schemas, services
from fermerce.core.schemas.response import IResponseMessage
from fermerce.app.users.user.models import User
from fermerce.app.users.user import dependency


router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    data_in: schemas.IVendorIn,
    request: Request,
    user=Depends(dependency.require_user),
):
    return await services.create(data_in=data_in, request=request, user=user)


@router.put("/{vendor_id}", status_code=status.HTTP_200_OK)
async def update_vendor_details(
    data_in: schemas.IVendorIn,
    vendor_id: uuid.UUID,
    request: Request,
    user=Depends(dependency.require_vendor),
):
    return await services.update(
        data_in=data_in, request=request, vendor_id=vendor_id, user=user
    )


@router.get(
    "/{vendor_id}",
    response_model=t.Union[schemas.IVendorOutFull, schemas.IVendorOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependency.require_user)],
)
async def get_vendor(
    vendor_id: uuid.UUID,
    load_related: bool = True,
):
    return await services.get_vendor_details(vendor_id, load_related)
