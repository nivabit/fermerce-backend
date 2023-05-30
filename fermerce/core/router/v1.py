from fastapi import APIRouter
from fermerce.lib.utils import get_api_prefix

from fermerce.app.users.user.api.v1 import router as users_api_router
from fermerce.app.products.product.api.v1 import router as products_api_router
from fermerce.app.products.product_detail.api.v1 import (
    router as product_details_api_router,
)
from fermerce.app.users.auth.api.v1 import router as auth_api_router
from fermerce.app.products.category.api.v1 import router as category_api_router
from fermerce.app.markets.country.api.v1 import router as country_api_router
from fermerce.app.markets.state.api.v1 import router as state_api_router
from fermerce.app.business.vendor.api.v1 import router as business_api_router
from fermerce.app.products.measuring_unit.api.v1 import (
    router as measurement_unit_api_router,
)
from fermerce.app.products.reviews.api.v1 import (
    router as review_unit_api_router,
)
from fermerce.app.products.promo_code.api.v1 import (
    router as promotion_code_api_router,
)
from fermerce.app.products.selling_units.api.v1 import (
    router as selling_units_router,
)
from fermerce.app.markets.status.api.v1 import router as status_api_router
from fermerce.app.medias.api.v1 import router as medias_api_router
from fermerce.app.users.address.api.v1 import (
    router as shipping_address_api_router,
)
from fermerce.app.markets.cart.api.v1 import router as cart_api_router


from fermerce.app.markets.order.api.v1 import router as order_api_router

from fermerce.app.markets.tracking.api.v1 import router as tracking_api_router
from fermerce.app.business.message.api.v1 import router as message_api_router

from fermerce.app.payment.api.v1 import router as payment_api_router

router = APIRouter(prefix=get_api_prefix.get_prefix())
router.include_router(router=users_api_router)
router.include_router(router=auth_api_router)
router.include_router(router=shipping_address_api_router)
router.include_router(router=country_api_router)
router.include_router(router=state_api_router)
router.include_router(router=status_api_router)
router.include_router(router=category_api_router)
router.include_router(router=measurement_unit_api_router)
router.include_router(router=products_api_router)
router.include_router(router=product_details_api_router)
router.include_router(router=selling_units_router)
router.include_router(router=promotion_code_api_router)
router.include_router(router=business_api_router)
router.include_router(router=medias_api_router)
router.include_router(router=cart_api_router)
router.include_router(router=order_api_router)
router.include_router(router=review_unit_api_router)
router.include_router(router=tracking_api_router)
router.include_router(router=message_api_router)
router.include_router(router=payment_api_router)
