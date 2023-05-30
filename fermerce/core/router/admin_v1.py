from fastapi import APIRouter
from fermerce.lib.utils import get_api_prefix

from fermerce.app.users.user.api.admin_v1 import router as users_api_router

from fermerce.app.users.permission.api.v1 import router as permission_api_router
from fermerce.app.business.vendor.api.admin_v1 import (
    router as business_vendor_api_router,
)
from fermerce.app.products.reviews.api.admin_v1 import (
    router as product_review_api_router,
)
from fermerce.app.users.staff.api.v1 import router as staff_api_router
from fermerce.app.markets.status.api.admin_v1 import router as status_api_router
from fermerce.app.markets.delivery_mode.api.v1 import (
    router as delivery_model_api_router,
)
from fermerce.app.markets.order.api.admin_v1 import router as order_api_router

from fermerce.app.payment.api.admin_v1 import router as payment_api_router


router = APIRouter(prefix=f"{get_api_prefix.get_prefix()}")
router.include_router(router=permission_api_router)
router.include_router(router=users_api_router)
router.include_router(router=staff_api_router)
router.include_router(router=status_api_router)
router.include_router(router=delivery_model_api_router)
router.include_router(router=business_vendor_api_router)
router.include_router(router=order_api_router)
router.include_router(router=product_review_api_router)
router.include_router(router=payment_api_router)
