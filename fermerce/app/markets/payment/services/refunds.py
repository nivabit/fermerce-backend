from fermerce.app.markets.status.models import Status
from fermerce.app.users.user.models import User
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.errors import error
from fermerce.app.markets.payment import models
from fermerce.lib.utils.paystack.refund import services, schemas as refund_schemas


async def refund_charges(
    data_in: refund_schemas.RefundTransactionIn,
    user: User,
) -> IResponseMessage:
    get_payment = await models.Payment.get_or_none(
        reference=data_in.reference, user=user
    )
    if get_payment:
        if get_payment.total < data_in.amount:
            raise error.BadDataError("the refund payment amount is out of range")
        response = await services.create_refund(data_in=data_in)
        if response.status and response.data.deducted_amount > 0:
            get_status = await Status.get_or_create(name="refunded")
            get_payment.update_from_dict({"status": get_status})
            await get_payment.save()
            return IResponseMessage(message="payment was refunded successful")
        raise error.BadDataError(response.message)
    raise error.ServerError("error refunding payment")


async def get_refund(payment_reference: str, user: User) -> refund_schemas.IRefundData:
    get_payment = await models.Payment.get_or_none(
        reference=payment_reference,
        user=user,
    )
    if get_payment:
        response = await services.get_refund(payment_reference)
        if response.status:
            return response.data
        raise error.BadDataError(response.message)
    raise error.ServerError("error refunding payment")
