import uuid
import typing as t
from tortoise.expressions import Q
from fermerce.app.vendor.models import Vendor
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.recipient import models, schemas
from fermerce.lib.paystack.recipient.services import delete_trans_recipient
from fermerce.taskiq.vendor_verification.tasks import verify_vendor_account


async def add_vendor_bank(
    data_in: schemas.IBankIn,
    vendor: Vendor,
) -> IResponseMessage:
    check_vendor_bank = await models.BankDetail.get_or_none(vendor=vendor)
    if check_vendor_bank:
        raise error.BadDataError(
            f"Bank detail already exist for business {vendor.business_name}"
        )
    new_bank_details = models.BankDetail.create(
        vendor=vendor, **data_in.dict(exclude={"vendor_id"})
    )
    if new_bank_details:
        # add verification process
        new_verification_process = await models.VendorVerification.create(
            bank=new_bank_details,
            vendor=vendor,
            # if the account owner is business (discus with team add it here)
        )
        if new_verification_process and new_bank_details:
            await verify_vendor_account.kiq(vendor_id=vendor.id)
            return IResponseMessage(
                message="business account was added successfully"
            )
    raise error.ServerError("error refunding payment")


async def update_vendor_bank(
    bank_detail_id: uuid.UUID,
    data_in: schemas.IBankIn,
    vendor: Vendor,
) -> IResponseMessage:
    check_vendor_bank = await models.BankDetail.get_or_none(
        vendor=vendor, id=bank_detail_id
    )
    if not check_vendor_bank:
        raise error.NotFoundError(
            f"Bank detail does not exist for business {vendor.business_name}"
        )
    check_vendor_bank.update_from_dict(
        vendor=vendor,
        **data_in.dict(exclude={"vendor_id"}),
    )
    await check_vendor_bank.save()
    get_recipient = await models.Recipient.get_or_none(vendor=vendor)
    if get_recipient:
        result = await delete_trans_recipient(
            recipient_code=get_recipient.recipient_code
        )
        if result and result.get("status", False) != False:
            await get_recipient.delete()
            await verify_vendor_account.kiq(vendor_id=vendor.id)
            return IResponseMessage(
                message="business account was updated successfully"
            )
    raise error.ServerError("error updating bank details")


async def get_single_bank_detail(
    bank_details_id: uuid.UUID,
    load_related: bool = False,
) -> models.BankDetail:
    query = models.BankDetail
    query = query.filter(id=bank_details_id)
    result = await filter_and_single(
        model=models.BankDetail,
        query=query,
        load_related=load_related,
        order_by="id",
    )
    if not result:
        raise error.NotFoundError("bank detail not found")
    return result


async def list_bank_details_list(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
    vendor: Vendor = None,
) -> t.List[models.BankDetail]:
    query = models.BankDetail
    if vendor:
        query = query.filter(vendor=vendor).select_related(
            "payment", "payment__user"
        )
    if filter_string:
        query = query.filter(
            Q(bank_name__icontains=filter_string)
            | Q(vendor__business_name__icontains=filter_string)
            | Q(bank_code__icontains=filter_string)
            | Q(account_name__icontains=filter_string)
            | Q(country_code__icontains=filter_string)
            | Q(country_code__icontains=filter_string)
        )

    return await filter_and_list(
        model=models.BankDetail,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )
