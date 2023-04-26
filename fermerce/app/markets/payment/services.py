from datetime import date
import typing as t
import uuid
from fermerce.app.users.user.model import User
from core.enum.frequent_duration import Frequent
from core.enum.sort_type import SortOrder
from core.schema.response import IResponseMessage
from lib.errors import error
from fastapi import status, Response
from fermerce.app.market.payment import schema, model
from core.settings import config
from fermerce.app.market.payment import utils
from fermerce.app.market.payment.repository import payment_repo
from fermerce.app.market.order.repository import order_repo
from fermerce.app.products.reviews.repository import product_review_repo


async def create_payment(
    obj: schema.IPaymentIn,
    user: User,
) -> Response:
    get_order = await order_repo.get_by_attr(
        attr=dict(order_id=obj.order_id, user_id=user.id), first=True, load_related=True
    )

    if not get_order:
        raise error.NotFoundError("order not found")
    if not get_order.items:
        raise error.NotFoundError("No item for this order")
    total_price = utils.get_product_total_price(get_order.items)
    if total_price > 0:
        await payment_repo.create(order=get_order, total_payed=total_price)
        meta_data = schema.PaymentMeta(order_id=get_order.order_id, user_id=user.id)
        user = schema.User(
            email=user.email,
            name=f"{user.firstname} {user.lastname}",
            user_id=user.id,
            order_id=get_order.id,
        )
        payment_data = schema.PaymentLinkData(
            public_key=config.rave_public_key,
            tx_ref=get_order.order_id,
            amount=total_price,
            meta=meta_data.dict(),
            user=user.dict(),
            redirect_url=f"{config.project_url}/dashboard/payment/{get_order.order_id}",
        )
        data_out: schema.IPaymentResponse = await utils.generate_link(data_in=payment_data)
        if data_out.status == "success":
            return schema.IPaymentInitOut(
                paymentLink=data_out.data_in.link,
                total_amount=total_price,
            )
    raise error.ServerError("Error creating payment link")


async def get_payment(payment_id: uuid.UUID, user: User) -> model.Payment:
    get_payment = await payment_repo.get_by_attr(attr=dict(id=payment_id), load_related=True)
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


async def get_payment_revenue_trend() -> schema.IPaymentTrend:
    daily_sales = await payment_repo.get_total_sale_today()
    weekly_sales = await payment_repo.get_total_sale_this_week()
    monthly_sales = await payment_repo.get_total_sale_this_month()
    yearly_sales = await payment_repo.get_total_sale_this_year()
    return schema.IPaymentTrend(
        daily=daily_sales,
        weekly=weekly_sales,
        monthly=monthly_sales,
        yearly=yearly_sales,
    )


async def get_revenue_sum_in_date_range(
    data_in: schema.IPaymentRevenueInDateRange,
) -> t.Optional[float]:
    result = await payment_repo.get_sum_for_date_range(
        start_date=data_in.start_date, end_date=data_in.end_date, freq=data_in.freq
    )
    return result


async def verify_user_payment(
    data_in: schema.IVerifyPaymentResponse,
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
        check_payment: schema.IPaymentVerifyOut = utils.verify_payment(tx_ref=data_in.reference)
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
                await product_review_repo.create(obj=dict(user=user, product=product))
            return IResponseMessage(message="payment successful")
    except Exception:
        raise error.ServerError("verification failed")
