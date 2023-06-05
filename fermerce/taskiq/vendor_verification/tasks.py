from fermerce.taskiq.broker import broker
from fermerce.app.recipient import models
from fermerce.lib.paystack.verification import (
    services as p_verification_services,
    schemas as P_verification_schemas,
)
from fermerce.lib.paystack.recipient import services as p_recipient_services
from fermerce.app.message import models as message_models


@broker.task
async def create_recipient_account(vendor_id: dict):
    get_vendor_bank = await models.BankDetail.get_or_none(
        vendor__id=vendor_id
    ).select_related("business_account", "vendor")
    if get_vendor_bank and get_vendor_bank.verification:
        data = P_verification_schemas.IBankAccountValidateIn.from_orm(
            get_vendor_bank
        )
        new_recipient_account = (
            await p_recipient_services.create_trans_recipient(data_in=data)
        )
        if new_recipient_account.status:
            await models.Recipient.create(
                bank_detail=get_vendor_bank,
                recipient_code=new_recipient_account.data.recipient_code,
                is_deleted=new_recipient_account.data.active,
                vendor=get_vendor_bank.vendor,
            )
            await get_vendor_bank.verification.save()
        await message_models.Message.create(
            message=new_recipient_account.message
            if new_recipient_account.message
            else "Bank account verification failed",
            vendor=get_vendor_bank.vendor,
        )


@broker.task
async def verify_vendor_account(vendor_id: dict):
    get_vendor_bank = await models.BankDetail.get_or_none(
        vendor__id=vendor_id
    ).select_related("business_account", "vendor")
    if get_vendor_bank and get_vendor_bank.verification:
        data = P_verification_schemas.IBankAccountValidateIn.from_orm(
            get_vendor_bank
        )
        validate_vendor_account = (
            await p_verification_services.validate_account(data_in=data)
        )
        if validate_vendor_account and validate_vendor_account.status:
            get_vendor_bank.verification.update_from_dict(
                is_verified=validate_vendor_account.data.verified,
            )
            await get_vendor_bank.verification.save()
        await message_models.Message.create(
            message=validate_vendor_account.message
            if validate_vendor_account.message
            else "Bank account verification failed",
            vendor=get_vendor_bank.vendor,
        )
