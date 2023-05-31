import typing as t
import uuid
from fastapi import Response
from tortoise.expressions import Q
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.enum.sort_type import SearchType
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.business.vendor import schemas, models


async def create(data_in=schemas.IVendorIn):
    new_vendor = await models.Vendor.create()
    if new_vendor:
        return IResponseMessage(message="Vendor account was created successfully")
    raise error.ServerError("Error creating business account")


async def update(
    vendor: models.Vendor,
    data_in=schemas.IVendorIn,
):
    return IResponseMessage(message="Vendor account was updated successfully")
