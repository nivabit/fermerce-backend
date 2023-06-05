from fermerce.lib.paystack.verification import schemas
from fermerce.lib.paystack import client, endpoint
from fermerce.lib.errors import error


async def verify_account_number(data_in: schemas.IAccountResolveIn):
    try:
        response = await client.request.post(
            url=endpoint.get("bank").get("resolve"),
            params={
                "account_number": data_in.account_number,
                "bank_code": data_in.bank_code,
            },
        )
        data = schemas.IAccountResolveResponse(**response.json())
        return data
    except Exception:
        raise error.BadDataError(detail="Error refunding transaction")


async def validate_account(data_in: schemas.IBankAccountValidateIn):
    try:
        response = await client.request.post(
            url=endpoint.get("bank").get("validate"),
            json=data_in.json(),
        )
        data = schemas.IAccountVerificationResponse(response.json())
        return data
    except Exception:
        raise error.BadDataError(detail="Error refunding transaction")
