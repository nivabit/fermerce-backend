from datetime import date
import typing as t
import uuid
from tortoise.expressions import Q
from fermerce.app.markets.status.models import Status
from fermerce.app.markets.order.models import Order, OrderItem
from fermerce.app.users.user.models import User
from fermerce.core.enum.frequent_duration import Frequent
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.markets.payment import schemas, models
from fermerce.app.markets.payment import utils
from fermerce.lib.utils.paystack.charge import services, schemas as charge_schemas


async def create_order_charge(
    data_in: schemas.ICreateOrderPaymentIn,
    user: User,
) -> charge_schemas.IChargeRequest:
    get_order = await Order.get_or_none(id=data_in.order_id, user=user).select_related(
        "shipping_address", "payment"
    )
    if not get_order:
        raise error.NotFoundError("order not found")
    order_items = (
        await OrderItem.filter(order=get_order)
        .prefetch_related("selling_unit", "promo_codes")
        .all()
    )
    if not order_items:
        raise error.NotFoundError("No item for this order")
    if get_order.payment:
        raise error.BadDataError("This order has already been paid for")

    total_price = utils.get_product_total_price(order_items)
    if total_price > 0:
        get_status, _ = await Status.get_or_create(name="processing")
        new_payment = await models.Payment.create(
            order=get_order,
            total=total_price,
            user=user,
            status=get_status,
        )
        if new_payment:
            data_out = charge_schemas.IChargeRequest(
                email=user.email,
                amount=new_payment.total,
                reference=new_payment.reference,
            )
            return data_out
    raise error.ServerError("Error creating payment link")


async def create_charges_url(
    data_in: schemas.ICreateOrderPaymentIn,
    user: User,
) -> charge_schemas.IChargeRequestData:
    get_order = await Order.get_or_none(id=data_in.order_id, user=user).select_related(
        "shipping_address", "payment"
    )
    if not get_order:
        raise error.NotFoundError("order not found")
    order_items = (
        await OrderItem.filter(order=get_order)
        .prefetch_related("selling_unit", "promo_codes")
        .all()
    )
    if not order_items:
        raise error.NotFoundError("No item for this order")
    if get_order.payment:
        raise error.BadDataError("This order has already been paid for")

    total_price = utils.get_product_total_price(order_items)
    if total_price > 0:
        get_status, _ = await Status.get_or_create(name="processing")
        new_payment = await models.Payment.create(
            order=get_order,
            total=total_price,
            user=user,
            status=get_status,
        )
        if new_payment:
            data = charge_schemas.IChargeRequest(
                email=user.email,
                amount=new_payment.total,
                reference=new_payment.reference,
            )
            generate_url = await services.create_charge(data_in=data)
            if generate_url.status:
                return generate_url.data
            raise error.BadDataError(generate_url.message)
    raise error.ServerError("Error creating payment link")


async def verify_charges(
    data_in: schemas.IPaymentVerificationIn,
    user: User,
) -> IResponseMessage:
    get_unfinished_payment = await models.Payment.get_or_none(
        reference=data_in.reference,
        user=user,
    )
    if get_unfinished_payment:
        response = await services.charge_verification(get_unfinished_payment.reference)
        if response.status:
            get_status, _ = await Status.get_or_create(name="completed")
            get_unfinished_payment.update_from_dict({"status": get_status})
            await get_unfinished_payment.save()
            return IResponseMessage(message="payment verification was successful")
        raise error.BadDataError(response.message)
    raise error.ServerError("error validating payment")


async def get_charges(
    payment_id: uuid.UUID,
    user: User,
    load_related: bool = False,
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


async def list_charges(
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
