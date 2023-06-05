import uuid
import typing as t
from tortoise.expressions import Q
from fermerce.app.status.models import Status
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.charge import models as charge_models
from fermerce.app.refund import models, schemas
from fermerce.lib.paystack.refund import services as refund_services


async def refund_charges(
    data_in: schemas.RefundTransactionIn,
) -> IResponseMessage:
    get_payment = await charge_models.Payment.get_or_none(
        reference=data_in.reference,
    )
    if get_payment:
        if float(get_payment.total) < data_in.amount:
            raise error.BadDataError(
                "The refund payment amount is out of range"
            )
        response = await refund_services.create_refund(data_in=data_in)
        if response.status and response.data.deducted_amount > 0:
            new_refund = models.Refund.create(
                **schemas.IRefundData(**response.data.dict()).dict(),
                payment=get_payment
            )
            if new_refund:
                get_status = await Status.get_or_create(name="refunded")
                get_payment.update_from_dict({"status": get_status})
                await get_payment.save()
                return IResponseMessage(
                    message="payment was refunded successful"
                )
            error.ServerError("error refunding payment")
        raise error.BadDataError(response.message)
    raise error.ServerError("error refunding payment")


async def get_refund(
    refund_id: uuid.UUID,
    load_related: bool = False,
) -> models.Refund:
    query = models.Refund
    query = query.filter(id=refund_id)
    result = await filter_and_single(
        model=models.Refund,
        query=query,
        load_related=load_related,
        order_by="id",
    )
    if not result:
        raise error.NotFoundError("Payment not found")
    return result


async def list_refund(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
    user_id: uuid.UUID = None,
) -> t.List[models.Refund]:
    query = models.Refund
    if user_id:
        query = query.filter(user=user_id).select_related(
            "payment", "payment__user"
        )
    if filter_string:
        query = query.filter(
            Q(payment__user__email__icontains=filter_string)
            | Q(payment__reference__icontains=filter_string)
        )

    return await filter_and_list(
        model=models.Refund,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )
