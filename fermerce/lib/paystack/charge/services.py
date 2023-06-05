from fermerce.lib.paystack.charge import schemas
from fermerce.lib.paystack import client, endpoint
from fermerce.lib.errors import error


async def create_charge(data_in: schemas.IChargeRequest):
    try:
        response = await client.request.post(
            url=endpoint.get("transaction").get("create"), json=data_in.dict()
        )
        data = schemas.IChargeRequestOut(**response.json())
        return data
    except Exception:
        raise error.ServerError("Error creating payment request")


async def create_authorized_charge(data_in: schemas.ISavedCardChargeIn):
    try:
        response = await client.request.post(
            url=endpoint.get("transaction").get("authorized_charge"),
            json=data_in.dict(),
        )
        data: schemas.IChargeRequestOut = response.json()
        return data
    except Exception:
        raise error.ServerError("Error creating payment request")


async def charge_verification(payment_reference: str):
    try:
        url = f'{endpoint.get("transaction").get("verify")}/{payment_reference}'
        response = await client.request.get(url=url)
        data = schemas.IChargeResponse(**response.json())
        return data
    except Exception as e:
        print(e)
        raise error.BadDataError("Error verifying payment transaction")
