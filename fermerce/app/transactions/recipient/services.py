import uuid
import typing as t
from fastapi import Response, status
from tortoise.expressions import Q
from fermerce.app.vendor.models import Vendor
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base_old import filter_and_list, filter_and_single
from fermerce.lib.exceptions import exceptions
from fermerce.app.recipient import models, schemas
from fermerce.lib.paystack.recipient.services import delete_trans_recipient
from fermerce.taskiq.vendor_verification.tasks import verify_vendor_account


async def add_vendor_bank(
    data_in: schemas.IBankIn,
    vendor: Vendor,
) -> IResponseMessage:
    check_vendor_bank = await models.BankDetail.get_or_none(vendor=vendor)
    if check_vendor_bank:
        raise exceptions.BadDataError(
            f"Bank detail already exist for business {vendor.business_name}"
        )
    new_bank_details = await models.BankDetail.create(
        vendor=vendor, **data_in.dict(exclude={"vendor_id"})
    )
    if new_bank_details:
        # add verification process
        new_verification_process = await models.VendorVerification.create(
            account=new_bank_details,
            vendor=vendor,
            # if the account owner is business (discus with team add it here)
        )
        if new_verification_process and new_bank_details:
            await verify_vendor_account.kiq(vendor_id=vendor.id)
            return IResponseMessage(message="business account was added successfully")
    raise exceptions.ServerError("error refunding payment")


async def update_vendor_bank(
    bank_detail_id: uuid.UUID,
    data_in: schemas.IBankUpdateIn,
    vendor: Vendor,
) -> IResponseMessage:
    check_vendor_bank = await models.BankDetail.get_or_none(
        vendor=vendor, id=bank_detail_id
    ).select_related("verification")
    if not check_vendor_bank:
        raise exceptions.NotFoundError(
            f"Bank detail does not exist for business {vendor.business_name}"
        )
    check_bank_account = await models.BankDetail.get_or_none(
        vendor=vendor,
        type=data_in.type,
        currency=data_in.currency,
        bank_code=data_in.bank_code,
        account_number=data_in.account_number,
        account_name=data_in.account_name,
    )

    if check_bank_account and check_bank_account.id == bank_detail_id:
        return check_bank_account
    else:
        check_vendor_bank.update_from_dict(
            dict(
                vendor=vendor,
                **data_in.dict(exclude={"vendor_id"}),
            )
        )
        await check_vendor_bank.save()
        check_vendor_bank.verification.update_from_dict(dict(is_verified=False))
        await check_vendor_bank.verification.save()
        get_recipient = await models.Recipient.get_or_none(vendor=vendor)
        if get_recipient:
            result = await delete_trans_recipient(
                recipient_code=get_recipient.recipient_code
            )
            if result and result.get("status", False):
                get_recipient.update_from_dict(dict(is_deleted=True))
                await get_recipient.save()
                await verify_vendor_account.kiq(vendor_id=vendor.id)
                return IResponseMessage(
                    message="business account was updated successfully"
                )
        else:
            await verify_vendor_account.kiq(vendor_id=vendor.id)
            return IResponseMessage(message="business account was updated successfully")
    raise exceptions.ServerError("error updating bank details")


async def get_single_bank_detail(
    bank_detail_id: uuid.UUID, load_related: bool = False, vendor: Vendor = None
) -> models.BankDetail:
    query = models.BankDetail
    query = query.filter(id=bank_detail_id)
    if vendor:
        query = query.filter(vendor=vendor)
    result = await filter_and_single(
        model=models.BankDetail,
        query=query,
        load_related=load_related,
        order_by="id",
    )
    if not result:
        raise exceptions.NotFoundError("bank detail not found")
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
    is_verified: bool = False,
) -> t.List[models.BankDetail]:
    query = models.BankDetail
    if vendor:
        query = query.filter(
            vendor=vendor,
        ).select_related("payment", "payment__user")
    if filter_string:
        query = query.filter(
            Q(bank_name__icontains=filter_string)
            | Q(vendor__business_name__icontains=filter_string)
            | Q(bank_code__icontains=filter_string)
            | Q(account_name__icontains=filter_string)
            | Q(country_code__icontains=filter_string)
            | Q(country_code__icontains=filter_string),
        )
    query = query.filter(
        verification__is_verified=is_verified,
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


async def delete_bank_detail(bank_detail_id: uuid.UUID) -> None:
    get_bank_details = await models.BankDetail.get_or_none(
        id=bank_detail_id
    ).select_related("verification", "vendor")
    if get_bank_details:
        get_recipient = await models.Recipient.get_or_none(
            vendor=get_bank_details.vendor
        )
        if get_recipient:
            result = await delete_trans_recipient(
                recipient_code=get_recipient.recipient_code
            )
            if result and result.get("status", False):
                get_recipient.update_from_dict(dict(is_deleted=True))
                await get_recipient.save()
        get_bank_details.verification.update_from_dict(dict(is_verified=False))
        await get_bank_details.verification.save()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise exceptions.NotFoundError("Bank Detail not found")


async def suspend_account(
    bank_detail_id: uuid.UUID, suspend: bool = False
) -> IResponseMessage:
    get_verification = await models.VendorVerification.get_or_none(
        account__id=bank_detail_id
    )
    if get_verification and suspend:
        get_verification.update_from_dict(dict(is_verified=False))
        await get_verification.save()
        return IResponseMessage(message="account was successfully suspended")
    elif get_verification and not suspend:
        get_verification.update_from_dict(dict(is_verified=True))
        await get_verification.save()
        return IResponseMessage(message="account suspension was successfully removed")
    if not get_verification:
        raise exceptions.NotFoundError("account does not exist")
    raise exceptions.NotFoundError("Bank Detail not found")
