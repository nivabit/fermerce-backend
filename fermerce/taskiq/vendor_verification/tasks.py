import uuid
from fermerce.taskiq.broker import broker
from fermerce.app.recipient import models
from fermerce.lib.paystack.verification import (
    services as p_verification_services,
    schemas as P_verification_schemas,
)
from fermerce.lib.paystack.recipient import (
    services as p_recipient_services,
    schemas as P_recipient_schemas,
)
from fermerce.app.message import models as message_models


@broker.task
async def create_recipient_account(vendor_id: uuid.UUID):
    get_vendor_bank = await models.BankDetail.get_or_none(
        vendor__id=vendor_id
    ).select_related("verification", "vendor")
    if (
        get_vendor_bank
        and get_vendor_bank.verification
        and get_vendor_bank.verification.is_verified
    ):
        data = P_recipient_schemas.ITransactionRecipientIn(
            account_number=get_vendor_bank.account_number,
            name=get_vendor_bank.account_name,
            bank_code=get_vendor_bank.bank_code,
            type=get_vendor_bank.type,
            currency=get_vendor_bank.currency,
        )
        new_recipient_account = await p_recipient_services.create_trans_recipient(
            data_in=data
        )

        if new_recipient_account.status:
            check_recipient = await models.Recipient.get_or_none(
                vendor=get_vendor_bank.vendor
            )
            if check_recipient:
                check_recipient.update_from_dict(
                    dict(
                        bank_detail=get_vendor_bank,
                        recipient_code=new_recipient_account.data.recipient_code,
                        is_deleted=new_recipient_account.data.active,
                    )
                )
                await check_recipient.save()
            else:
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
            else "Fermerce payment account failed to create",
            vendor=get_vendor_bank.vendor,
        )


@broker.task
async def verify_vendor_account(vendor_id: dict):
    get_vendor_bank = await models.BankDetail.get_or_none(
        vendor__id=vendor_id
    ).select_related("verification", "vendor")
    if get_vendor_bank and get_vendor_bank.verification:
        data = P_verification_schemas.IAccountResolveIn.from_orm(get_vendor_bank)
        validate_vendor_account = await p_verification_services.verify_account_number(
            data_in=data
        )
        if validate_vendor_account and validate_vendor_account.status:
            response_name = validate_vendor_account.data.account_name.lower().split(" ")
            set_name = get_vendor_bank.account_name.lower().split(" ")
            is_present = all(item in response_name for item in set_name)
            if is_present:
                # TODO: check if the name on the bvn also match the name on the resolve account
                get_vendor_bank.verification.update_from_dict(
                    dict(
                        is_verified=validate_vendor_account.status,
                    )
                )
                await get_vendor_bank.verification.save()
                if is_present and get_vendor_bank:
                    await create_recipient_account(vendor_id=get_vendor_bank.vendor.id)
                    await message_models.Message.create(
                        message="bank details was verified successfully",
                        vendor=get_vendor_bank.vendor,
                    )
                await message_models.Message.create(
                    message="Could not verify bank details",
                    vendor=get_vendor_bank.vendor,
                )
        else:
            await message_models.Message.create(
                message="Could not verify bank details, please try again",
                vendor=get_vendor_bank.vendor,
            )
