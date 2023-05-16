from datetime import date
import typing as t
import uuid
from fermerce.app.markets.order.models import Order
from fermerce.app.users.user.models import User
from core.enum.frequent_duration import Frequent
from core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from lib.errors import error
from fastapi import status, Response
from fermerce.app.markets.payment import schemas, models
from fermerce.core.settings import config
from fermerce.app.markets.payment import utils
from fermerce.app.markets.payment.repository import payment_repo


async def create_payment(
    obj: schemas.IPaymentIn,
    user: User,
) -> Response:
    get_order = await Order.get_or_none(
        id=obj.order_id, user=user
    ).prefetch_related("items")
    if not get_order:
        raise error.NotFoundError("order not found")
    if not get_order.items:
        raise error.NotFoundError("No item for this order")
    total_price = utils.get_product_total_price(get_order.items)
    if total_price > 0:
        await models.Payment.create(order=get_order, total_payed=total_price)
        meta_data = schemas.PaymentMeta(
            order_id=get_order.order_id, user_id=user.id
        )
        user = schemas.User(
            email=user.email,
            name=f"{user.firstname} {user.lastname}",
            user_id=user.id,
            order_id=get_order.id,
        )
        payment_data = schemas.PaymentLinkData(
            public_key=config.rave_public_key,
            tx_ref=get_order.order_id,
            amount=total_price,
            meta=meta_data.dict(),
            user=user.dict(),
            redirect_url=f"{config.project_url}/dashboard/payment/{get_order.order_id}",
        )
        data_out: schemas.IPaymentResponse = await utils.generate_link(
            data_in=payment_data
        )
        if data_out.status == "success":
            return schemas.IPaymentInitOut(
                paymentLink=data_out.data_in.link,
                total_amount=total_price,
            )
    raise error.ServerError("Error creating payment link")


async def get_payment(payment_id: uuid.UUID, user: User) -> model.Payment:
    get_payment = await payment_repo.get_by_attr(
        attr=dict(id=payment_id), load_related=True
    )
    if get_payment and get_payment.order.user_id != user.id:
        raise error.NotFoundError("Payment not found")
    return get_payment


async def payment_list(
    user: User,
    filter: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
) -> t.List[model.Payment]:
    return await payment_repo.filter(
        filter_string=filter,
        per_page=per_page,
        page=page,
        select_columns=select,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
        strict_search=dict(user_id=user.id),
    )


async def delete_payment(payment_id: str) -> None:
    get_payment = await payment_repo.get(id=payment_id)
    if not get_payment:
        raise error.NotFoundError("payment not found")
    await payment_repo.delete(id=payment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_payment_revenue_trend() -> schemas.IPaymentTrend:
    daily_sales = await payment_repo.get_total_sale_today()
    weekly_sales = await payment_repo.get_total_sale_this_week()
    monthly_sales = await payment_repo.get_total_sale_this_month()
    yearly_sales = await payment_repo.get_total_sale_this_year()
    return schemas.IPaymentTrend(
        daily=daily_sales,
        weekly=weekly_sales,
        monthly=monthly_sales,
        yearly=yearly_sales,
    )


async def get_revenue_sum_in_date_range(
    data_in: schemas.IPaymentRevenueInDateRange,
) -> t.Optional[float]:
    result = await payment_repo.get_sum_for_date_range(
        start_date=data_in.start_date,
        end_date=data_in.end_date,
        freq=data_in.freq,
    )
    return result


async def verify_user_payment(
    data_in: schemas.IVerifyPaymentResponse,
    user: User,
):
    get_payment = await payment_repo.get_by_attr(
        attr=dict(reference=data_in.reference, user=user), first=True
    )
    if not get_payment:
        raise error.BadDataError("Invalid payment details was provided")
    if get_payment.completed:
        raise error.BadDataError("Invalid payment details was provided")
    try:
        check_payment: schemas.IPaymentVerifyOut = utils.verify_payment(
            tx_ref=data_in.reference
        )
        if check_payment.error:
            raise error.BadDataError("verification failed")
        get_order = await order_repo.get_by_attr(
            attr=dict(reference=data_in.reference, user=user), first=True
        )
        if not get_order:
            raise error.NotFoundError("order not found")
        if get_order.order_id != get_payment.reference:
            raise error.BadDataError("Invalid payment details was provided")
        update_payment = await payment_repo.update(
            id=get_payment.id,
            obj=dict(completed=True, total_payed=check_payment.amount),
        )

        if update_payment:
            for product in get_order.items:
                await product_review_repo.create(
                    obj=dict(user=user, product=product)
                )
            return IResponseMessage(message="payment successful")
    except Exception:
        raise error.ServerError("verification failed")
