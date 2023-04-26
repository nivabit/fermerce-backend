import uuid
from fastapi import APIRouter, Depends, Query, status
from src.app.market.payment import service, schema
from src.app.users.user.model import User
from core.enum.sort_type import SortOrder
from core.schema.response import IResponseMessage
from src.app.users.user import dependency

router = APIRouter(prefix="/payments", tags=["User payments"])


@router.get(
    "/trends",
    status_code=status.HTTP_200_OK,
    response_model=schema.IPaymentTrend,
)
async def get_payment_revenue_trend():
    return await service.get_payment_revenue_trend()


@router.post(
    "/revenue/sum_in_date_range",
    status_code=status.HTTP_200_OK,
    response_model=schema.IPaymentTrend,
)
async def get_revenue_sum_in_date_range(data_in: schema.IPaymentRevenueInDateRange):
    return await service.get_revenue_sum_in_date_range(data_in=data_in)
