from fastapi import APIRouter
from fermerce.lib.utils import get_api_prefix
from fermerce.app.user.api.v1 import (
    router as users_api_router,
    auth as users_auth_router,
)
from fermerce.app.product.api.v1 import router as products_api_router
from fermerce.app.product_detail.api.v1 import (
    router as product_details_api_router,
)
from fermerce.app.recipient.api.v1 import (
    router as router_recipient_api_router,
)
from fermerce.app.category.api.v1 import router as category_api_router
from fermerce.app.country.api.v1 import router as country_api_router
from fermerce.app.state.api.v1 import router as state_api_router
from fermerce.app.vendor.api.v1 import (
    router as business_api_router,
    auth as vendor_auth,
)
from fermerce.app.measuring_unit.api.v1 import (
    router as measurement_unit_api_router,
)
from fermerce.app.reviews.api.v1 import (
    router as review_unit_api_router,
)
from fermerce.app.promo_code.api.v1 import (
    router as promotion_code_api_router,
)
from fermerce.app.selling_units.api.v1 import (
    router as selling_units_router,
)
from fermerce.app.refund.api.v1 import (
    router as refund_payment_api_router,
)
from fermerce.app.cards.api.v1 import (
    router as save_cards_api_router,
)
from fermerce.app.status.api.v1 import router as status_api_router
from fermerce.app.medias.api.v1 import router as medias_api_router
from fermerce.app.address.api.v1.shipping_address import (
    router as shipping_address_api_router,
)
from fermerce.app.address.api.v1.vendor_v1 import (
    router as business_address_api_router,
)
from fermerce.app.cart.api.v1 import router as cart_api_router


from fermerce.app.order.api.v1 import router as order_api_router

from fermerce.app.tracking.api.v1 import router as tracking_api_router
from fermerce.app.message.api.v1 import router as message_api_router

from fermerce.app.charge.api.v1 import router as payment_api_router

router = APIRouter(prefix=get_api_prefix.get_prefix())
router.include_router(router=users_api_router)
router.include_router(router=users_auth_router)
router.include_router(router=shipping_address_api_router)

router.include_router(router=country_api_router)
router.include_router(router=state_api_router)
router.include_router(router=status_api_router)
router.include_router(router=category_api_router)
router.include_router(router=measurement_unit_api_router)
router.include_router(router=products_api_router)
router.include_router(router=router_recipient_api_router)
router.include_router(router=product_details_api_router)
router.include_router(router=selling_units_router)
router.include_router(router=save_cards_api_router)
router.include_router(router=promotion_code_api_router)
router.include_router(router=business_api_router)
router.include_router(router=vendor_auth)
router.include_router(router=business_address_api_router)
router.include_router(router=medias_api_router)
router.include_router(router=cart_api_router)
router.include_router(router=order_api_router)
router.include_router(router=refund_payment_api_router)
router.include_router(router=review_unit_api_router)
router.include_router(router=tracking_api_router)
router.include_router(router=message_api_router)
router.include_router(router=payment_api_router)
