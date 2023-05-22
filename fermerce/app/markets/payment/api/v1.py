import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from fermerce.app.markets.payment import services, schemas
from fermerce.app.users.user import dependency
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage

# from src.lib.shared.dependency import UserWrite

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ICardChargeOut,
)
async def create_payment(
    data_in: schemas.IPaymentCardIn,
    request: Request,
    user: User = Depends(dependency.require_user),
):
    return await services.create_payment(
        data_in=data_in,
        user=user,
        request=request,
    )


@router.post(
    "/validate",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ICardChargeOut,
)
async def validate_payment(
    data_in: schemas.IValidatedPaymentIn,
    user: User = Depends(dependency.require_user),
):
    return await services.validate_payment(
        data_in=data_in,
        user=user,
    )


@router.get("/{payment_id}", status_code=status.HTTP_200_OK)
async def get_payment_by_id(
    payment_id: uuid.UUID,
    load_related: bool = False,
    user: User = Depends(dependency.require_user),
):
    return await services.get_payment(
        payment_id=payment_id,
        user=user,
        load_related=load_related,
    )


@router.post("/verify", status_code=status.HTTP_200_OK, response_model=IResponseMessage)
async def verify_payment(
    order_id: uuid.UUID,
    user: User = Depends(dependency.require_user),
):
    return await services.verify_payment(order_id=order_id, user=user)
