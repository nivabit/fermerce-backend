import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.markets.payment import services, schemas
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.app.users.user import dependency

router = APIRouter(prefix="/payments", tags=["User payments"])


@router.post("/refund", status_code=status.HTTP_200_OK, response_model=IResponseMessage)
async def verify_payment(
    data_in: schemas.IRefundDataIn,
    user: User = Depends(dependency.require_user),
):
    return await services.refund_payment(data_in=data_in, user=user)


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
    return await services.filter(
        select=select,
        filter_string=filter_string,
        user=user,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


# @router.get(
#     "/trends",
#     status_code=status.HTTP_200_OK,
#     response_model=schema.IPaymentTrend,
# )
# async def get_payment_revenue_trend():
#     return await service.get_payment_revenue_trend()


# @router.post(
#     "/revenue/sum_in_date_range",
#     status_code=status.HTTP_200_OK,
#     response_model=schema.IPaymentTrend,
# )
# async def get_revenue_sum_in_date_range(
#     data_in: schema.IPaymentRevenueInDateRange,
# ):
#     return await service.get_revenue_sum_in_date_range(data_in=data_in)
