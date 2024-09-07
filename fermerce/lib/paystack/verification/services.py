from fermerce.lib.paystack.verification import schemas
from fermerce.lib.paystack import client, endpoint
from fermerce.lib.exceptions import exceptions


async def verify_account_number(data_in: schemas.IAccountResolveIn):
    try:
        response = await client.request.get(
            url=endpoint.get("bank").get("resolve"),
            params={
                "account_number": data_in.account_number,
                "bank_code": data_in.bank_code,
            },
        )
        data = schemas.IAccountResolveResponse(**response.json())
        return data

    except Exception:
        raise exceptions.BadDataError(detail="Error validating account")


async def validate_account(data_in: schemas.IBankAccountValidateIn):
    try:
        response = await client.request.post(
            url=endpoint.get("bank").get("validate"),
            json=data_in.dict(),
        )

        data = schemas.IAccountVerificationResponse(**response.json())
        print(response.json())
        return data

    except Exception as e:
        raise exceptions.BadDataError(detail="Error refunding transaction")
