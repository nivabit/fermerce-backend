from fermerce.lib.utils.paystack.verification import schemas
from fermerce.lib.utils.paystack import client, endpoint
from fermerce.lib.errors import error


async def verify_account(data_in: schemas.IAccountResolveIn):
    try:
        response = await client.request.post(
            url=endpoint.get("bank").get("resolve"),
            params={
                "account_number": data_in.account_number,
                "bank_code": data_in.bank_code,
            },
        )
        data: schemas.IAccountResolveResponse = response.json()
        return data
    except Exception:
        raise error.BadDataError(detail="Error refunding transaction")


async def validate_account(data_in: schemas.IBankAccountValidateIn):
    try:
        response = await client.request.post(
            url=endpoint.get("bank").get("resolve"),
            params={
                "account_number": data_in.account_number,
                "bank_code": data_in.bank_code,
            },
        )
        data = schemas.IAccountVerificationResponse(response.json())
        return data
    except Exception:
        raise error.BadDataError(detail="Error refunding transaction")
