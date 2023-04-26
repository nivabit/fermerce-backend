# import all apps model to this file for alembic migration access
from fermerce.app.users.user.models import User

from fermerce.app.users.staff.models import Staff
from fermerce.app.users.permission.models import Permission

from fermerce.app.users.auth.models import Auth
from fermerce.app.markets.country.models import Country
from fermerce.app.markets.state.models import State
from fermerce.app.products.selling_units.models import ProductSellingUnit

from fermerce.app.markets.cart.models import Cart
from fermerce.app.markets.delivery_mode.models import DeliveryMode

from fermerce.app.markets.order.models import Order, OrderItem

# from fermerce.app.markets.payment.model import Payment
from fermerce.app.business.vendor.models import Vendor
from fermerce.app.medias.models import Media
from fermerce.app.users.address.models import ShippingAddress
from fermerce.app.products.measuring_unit.models import MeasuringUnit
from fermerce.app.products.promo_code.models import ProductPromoCode
from fermerce.app.products.category.models import ProductCategory
from fermerce.app.products.reviews.models import Review
from fermerce.app.markets.status.models import Status
from fermerce.app.products.product.models import Product, ProductDetail
from fermerce.app.markets.tracking.models import Tracking
