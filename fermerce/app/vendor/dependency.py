from fastapi import Depends
from fermerce.app.vendor.models import Vendor
from fermerce.lib.shared.dependency import AppAuth
from fermerce.lib.errors import error
from fermerce.app.vendor import services


async def require_vendor(
    get_user: dict = Depends(AppAuth.authenticate),
):
    vendor = await Vendor.get_or_none(id=get_user.get("user_id", None))
    if vendor:
        return vendor
    raise error.UnauthorizedError()


async def require_vendor_full_data(
    get_user: dict = Depends(AppAuth.authenticate),
):
    vendor = await services.get_vendor_details(
        vendor_id=get_user.get("user_id", None), load_related=True
    )
    if vendor:
        return vendor
    raise error.UnauthorizedError()
