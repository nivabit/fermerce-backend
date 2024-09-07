import uuid
import typing as t
from fastapi import APIRouter, Depends, Query, Request, status
from fermerce.app.charge import schemas
from fermerce.app.charge import services
from fermerce.app.user import dependency
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.paystack.charge import schemas as charge_schemas

# from src.lib.shared.dependency import UserWrite

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=charge_schemas.IChargeRequest,
)
async def create_payment(
    data_in: schemas.ICreateOrderPaymentIn,
    user: User = Depends(dependency.require_user),
):
    return await services.create_order_charge(data_in=data_in, user=user)


@router.post(
    "/generate_link",
    status_code=status.HTTP_201_CREATED,
    # response_model=charge_schemas.IChargeRequestData,
)
async def create_payment(
    data_in: schemas.ICreateOrderPaymentIn,
    user: User = Depends(dependency.require_user),
):
    return await services.create_charges_url(data_in=data_in, user=user)


@router.get("/{payment_id}", status_code=status.HTTP_200_OK)
async def get_payment_by_id(
    payment_id: uuid.UUID,
    load_related: bool = False,
    user: User = Depends(dependency.require_user),
):
    return await services.get_charges(
        payment_id=payment_id,
        user=user,
        load_related=load_related,
    )


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=IResponseMessage,
)
async def verify_payment(
    data_in: schemas.IPaymentVerificationIn,
    user: User = Depends(dependency.require_user),
):
    return await services.verify_charges(data_in=data_in, user=user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=dict)
async def get_payment_list(
    user: User = Depends(dependency.require_user),
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    select: t.Optional[str] = Query(
        default="",
        alias="select",
        description="specific attributes of the permissions",
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
    load_related: bool = False,
):
    return await services.list_charges(
        select=select,
        filter_string=filter_string,
        user=user,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )
