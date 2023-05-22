from datetime import date
import typing as t
import uuid
from tortoise.expressions import Q
from fermerce.app.markets.status.models import Status
from fermerce.app.markets.order.models import Order, OrderItem
from fermerce.app.users.auth.models import Auth
from fermerce.app.users.user.models import User
from fermerce.core.enum.frequent_duration import Frequent
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fastapi import Request, status, Response
from fermerce.app.markets.payment import schemas, models
from fermerce.app.markets.payment import utils


async def create_payment(
    data_in: schemas.IPaymentCardIn,
    user: User,
    request: Request,
) -> Response:
    get_order = await Order.get_or_none(id=data_in.order_id, user=user).select_related(
        "shipping_address"
    )
    if not get_order:
        raise error.NotFoundError("order not found")
    order_items = await OrderItem.filter(order=get_order).all()
    if not order_items:
        raise error.NotFoundError("No item for this order")
    if get_order.payment:
        raise error.BadDataError("This order has already been paid for")
    phone_number: str = None
    if data_in.phonenumber:
        phone_number = data_in.phonenumber
    else:
        order_phones = get_order.shipping_address.phones.split(",")
        if order_phones:
            phone_number = order_phones[0]
        else:
            raise error.BadDataError("Phone number is  required")

    total_price = utils.get_product_total_price(order_items)
    ipaddress = Auth.get_user_ip(request)
    if total_price > 0:
        get_status = await Status.get_or_create(name="processing")
        new_payment = await models.Payment.create(
            order=get_order,
            total=total_price,
            user=user,
            status=get_status,
        )
        meta_data = schemas.IPaymentUserIn(
            email=user.email,
            firstname=user.firstname,
            lastname=user.lastname,
            phonenumber=phone_number,
            IP=ipaddress,
            txRef=new_payment.reference,
            amount=total_price,
        )

        response: schemas.ICardChargeResponse = utils.charge_card(
            data_in=data_in,
            user_detail=meta_data,
        )

        if not response.error:
            if response.validationRequired:
                new_payment.update_from_dict({"flwRef": response.flwRef})
                await new_payment.save()
                return schemas.ICardChargeOut(
                    order_id=get_order.id,
                    message="Charge was initialized successfully",
                )
    raise error.ServerError("Error creating payment link")


async def validate_payment(data_in: schemas.IValidatedPaymentIn, user: User):
    get_unfinished_payment = await models.Payment.get_or_none(
        order=data_in.order_id, user=user
    )
    if get_unfinished_payment:
        response = utils.charge_verification(
            {"otp": data_in.otp, "flwRef": get_unfinished_payment.flwRef}
        )
        if not response.error:
            response = utils.verify_payment(get_unfinished_payment.reference)
            if not response.error:
                get_status = await Status.get_or_create("completed")
                get_unfinished_payment.update_from_dict({"status": get_status})
                await get_unfinished_payment.save()
                return IResponseMessage(message="payment successful")
        raise error.UnauthorizedError("error validating payment")
    raise error.ServerError("error validating payment")


async def verify_payment(order_id: uuid.UUID, user: User):
    get_unfinished_payment = await models.Payment.get_or_none(order=order_id, user=user)
    if get_unfinished_payment:
        response = utils.verify_payment(get_unfinished_payment.reference)
        if not response.error:
            get_status = await Status.get_or_create("completed")
            get_unfinished_payment.update_from_dict({"status": get_status})
            await get_unfinished_payment.save()
            return IResponseMessage(message="payment successful")
        raise error.UnauthorizedError("error validating payment")
    raise error.ServerError("error validating payment")


async def refund_payment(data_in: schemas.IRefundDataIn, user: User):
    get_payment = await models.Payment.get_or_none(order=data_in.order_id, user=user)
    if get_payment:
        if get_payment.total < data_in.amount:
            raise error.BadDataError("the refund payment amount is out of range")
        response = utils.refund_payment(
            data_in={"amount": data_in.amount, "flwRef": get_payment.flwRef}
        )
        if response.status and response.data.AmountRefunded > 0:
            get_status = await Status.get_or_create("completed")
            get_payment.update_from_dict({"status": get_status})
            await get_payment.save()
            return IResponseMessage(message="payment was refunded successful")
    raise error.ServerError("error refunding payment")


async def get_payment(
    payment_id: uuid.UUID, user: User, load_related: bool = False
) -> models.Payment:
    query = models.Payment
    if user:
        query = query.filter(user=user, id=payment_id)
    result = await filter_and_single(
        model=models.Payment,
        query=query,
        load_related=load_related,
        order_by="id",
    )
    if not result:
        raise error.NotFoundError("Payment not found")
    return result


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
    user: User = None,
) -> t.List[models.Payment]:
    query = models.Payment
    if user:
        query = query.filter(user=user)
    if filter_string:
        query = query.filter(
            Q(flwRef__icontains=filter_string)
            | Q(reference__icontains=filter_string)
            | Q(order__order_id__icontains=filter_string)
        )

    return await filter_and_list(
        model=models.Payment,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )


# async def delete_payment(payment_id: str) -> None:
#     get_payment = await payment_repo.get(id=payment_id)
#     if not get_payment:
#         raise error.NotFoundError("payment not found")
#     await payment_repo.delete(id=payment_id)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# async def get_payment_revenue_trend() -> schemas.IPaymentTrend:
#     daily_sales = await payment_repo.get_total_sale_today()
#     weekly_sales = await payment_repo.get_total_sale_this_week()
#     monthly_sales = await payment_repo.get_total_sale_this_month()
#     yearly_sales = await payment_repo.get_total_sale_this_year()
#     return schemas.IPaymentTrend(
#         daily=daily_sales,
#         weekly=weekly_sales,
#         monthly=monthly_sales,
#         yearly=yearly_sales,
#     )


# async def get_revenue_sum_in_date_range(
#     data_in: schemas.IPaymentRevenueInDateRange,
# ) -> t.Optional[float]:
#     result = await payment_repo.get_sum_for_date_range(
#         start_date=data_in.start_date,
#         end_date=data_in.end_date,
#         freq=data_in.freq,
#     )
#     return result
