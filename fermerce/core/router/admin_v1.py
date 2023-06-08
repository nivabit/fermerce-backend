from fastapi import APIRouter
from fermerce.lib.utils import get_api_prefix

from fermerce.app.user.api.admin_v1 import router as users_api_router

from fermerce.app.permission.api.v1 import router as permission_api_router
from fermerce.app.vendor.api.admin_v1 import (
    router as business_vendor_api_router,
)
from fermerce.app.warehouse.api.v1 import router as warehouse_api_router
from fermerce.app.reviews.api.admin_v1 import (
    router as product_review_api_router,
)
from fermerce.app.recipient.api.admin_v1 import (
    router as vendor_recipient_api_router,
)
from fermerce.app.staff.api.v1 import router as staff_api_router
from fermerce.app.status.api.admin_v1 import router as status_api_router
from fermerce.app.delivery_mode.api.v1 import (
    router as delivery_model_api_router,
)
from fermerce.app.order.api.admin_v1 import router as order_api_router

from fermerce.app.charge.api.admin_v1 import router as payment_api_router


router = APIRouter(prefix=f"{get_api_prefix.get_prefix()}")
router.include_router(router=permission_api_router)
router.include_router(router=users_api_router)
router.include_router(router=vendor_recipient_api_router)
router.include_router(router=staff_api_router)
router.include_router(router=status_api_router)
router.include_router(router=delivery_model_api_router)
router.include_router(router=business_vendor_api_router)
router.include_router(router=order_api_router)
router.include_router(router=warehouse_api_router)
router.include_router(router=product_review_api_router)
router.include_router(router=payment_api_router)
