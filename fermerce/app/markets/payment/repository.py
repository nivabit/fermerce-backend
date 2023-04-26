from datetime import date, datetime, timedelta
from decimal import Decimal
import typing as t
from src.app.market.order.model import Order, OrderItem
import sqlalchemy as sa
from core.enum.frequent_duration import Frequent
from lib.errors import error

from core.repository.base import BaseRepository
from src.app.market.payment import model


class PaymentRepository(BaseRepository[model.Payment]):
    def __init__(self):
        super().__init__(model.Payment)

    def get_total_amount(self, items: t.List[OrderItem]):
        total_amount = 0
        for item in items:
            if item.pdf:
                total_amount += item.product

    async def create(self, order: Order, total_payed: Decimal) -> model.Payment:
        if not order and order.items:
            return
        new_payment: model.Payment = self.model(
            order=order,
            total_payed=total_payed,
            user=order.user,
            reference=order.order_id,
        )
        await self.db.add(new_payment)
        await self.db.commit()
        await self.db.refresh(new_payment)
        return new_payment

    async def get_total_sale_today(self) -> float:
        try:
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day)
            today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
            stmt = sa.select(sa.func.sum(self.model.total_payed)).where(
                self.model.created_at >= today_start,
                self.model.created_at <= today_end,
            )
            result = await self.db.execute(stmt).scalar()
            return result
        except:
            raise error.ServiceError("Error getting total payment")

    async def get_total_sale_this_week(self) -> float:
        try:
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            stmt = sa.select(sa.func.sum(self.model.total_payed)).where(
                self.model.created_at >= start_of_week,
                self.model.created_at <= end_of_week,
            )
            result = await self.db.execute(stmt).scalar()
            return result
        except:
            raise error.ServiceError("Error getting total payment")

    async def get_total_sale_this_month(self) -> float:
        try:
            today = date.today()
            start_of_month = date(today.year, today.month, 1)
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
            stmt = sa.select(sa.func.sum(self.model.total_payed)).where(
                self.model.created_at >= start_of_month,
                self.model.created_at <= end_of_month,
            )
            result = await self.db.execute(stmt).scalar()
            return result
        except:
            raise error.ServiceError("Error getting total payment")

    async def get_total_sale_this_year(self) -> float:
        try:
            year = datetime.now().year
            start_of_year = date(year, 1, 1)
            end_of_year = date(year, 12, 31)
            stmt = sa.select(sa.func.sum(self.model.total_payed)).where(
                self.model.created_at >= start_of_year,
                self.model.created_at <= end_of_year,
            )
            result = await self.db.execute(stmt).scalar()
            return result
        except:
            raise error.ServiceError("Error getting total payment")

    async def get_sum_for_date_range(
        self, start_date: date, end_date: date, freq: Frequent = Frequent.daily
    ) -> t.Optional[int]:
        sum_column = sa.func.sum(self.model.column_to_sum)
        if freq == Frequent.daily:
            stmt = (
                sa.select(sum_column)
                .where(self.model.created_at >= start_date)
                .where(self.model.created_at <= end_date)
            )
        elif freq == Frequent.weekly:
            start_of_week = start_date - timedelta(days=start_date.weekday())
            end_of_week = end_date + timedelta(days=6 - end_date.weekday())
            stmt = (
                sa.select(sum_column)
                .where(self.model.created_at >= start_of_week)
                .where(self.model.created_at <= end_of_week)
            )
        elif freq == Frequent.monthly:
            start_of_month = date(start_date.year, start_date.month, 1)
            end_of_month = date(end_date.year, end_date.month + 1, 1) - timedelta(
                days=1
            )
            stmt = (
                sa.select(sum_column)
                .where(self.model.created_at >= start_of_month)
                .where(self.model.created_at <= end_of_month)
            )
        elif freq == Frequent.yearly:
            start_of_year = date(start_date.year, 1, 1)
            end_of_year = date(end_date.year, 12, 31)
            stmt = (
                sa.select(sum_column)
                .where(self.model.created_at >= start_of_year)
                .where(self.model.created_at <= end_of_year)
            )
        else:
            raise ValueError("Invalid frequency specified.")

        result = await self.db.execute(stmt).scalar()
        return result


payment_repo = PaymentRepository()
