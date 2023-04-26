from lib.db.primary_key import GUID, Base, sa
from sqlalchemy.orm import relationship
from lib.utils.random_string import generate_orderId
from src.app.market.payment.enum import PaymentStatus


class Payment(Base):
    __tablename__ = "payment"
    reference = sa.Column(sa.String(18), default=lambda: generate_orderId(15))
    total = sa.Column(sa.Numeric(precision=10, scale=2))
    discount_given = sa.Column(sa.Float, default=0.0)
    user_id = sa.Column(GUID, sa.ForeignKey("user.id", ondelete="SET NULL"))
    user = relationship("User", back_populates="payments")
    status = sa.Column(sa.Enum(PaymentStatus), default=PaymentStatus.pending)
    order = relationship("Order", back_populates="payment", uselist=False)
