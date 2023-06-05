import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.charge import services
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.paystack.refund import schemas as charge_schemas
from fermerce.app.user import dependency

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/admin", status_code=status.HTTP_200_OK, response_model=dict)
async def get_payment_list_by_admin(
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
        user=None,
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
