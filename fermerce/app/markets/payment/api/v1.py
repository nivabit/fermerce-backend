import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from fermerce.app.markets.payment import schemas
from fermerce.app.markets.payment.services import charges
from fermerce.app.users.user import dependency
from fermerce.app.users.user.models import User
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.utils.paystack.charge import schemas as charge_schemas

# from src.lib.shared.dependency import UserWrite

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=charge_schemas.IChargeRequest,
)
async def create_payment(
    data_in: schemas.ICreateOrderPaymentIn,
    request: Request,
    user: User = Depends(dependency.require_user),
):
    return await charges.create_order_charge(
        data_in=data_in,
        user=user,
        request=request,
    )


@router.get("/{payment_id}", status_code=status.HTTP_200_OK)
async def get_payment_by_id(
    payment_id: uuid.UUID,
    load_related: bool = False,
    user: User = Depends(dependency.require_user),
):
    return await charges.get_payment(
        payment_id=payment_id,
        user=user,
        load_related=load_related,
    )


@router.post(
    "/{order_id}/verify",
    status_code=status.HTTP_200_OK,
    response_model=IResponseMessage,
)
async def verify_payment(
    data_in: schemas.IPaymentVerificationIn,
    user: User = Depends(dependency.require_user),
):
    return await charges.verify_charges(data_in=data_in, user=user)
