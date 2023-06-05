import typing as t
from fermerce.lib.paystack.recipient import schemas
from fermerce.lib.paystack import client, endpoint
from fermerce.lib.errors import error


async def create_trans_recipient(data_in: schemas.ITransactionRecipientIn):
    try:
        response = await client.request.post(
            url=endpoint.get("transfers_recipient").get("create"),
            json=data_in.dict(),
        )
        data = schemas.TransferRecipientResponse(**response.json())
        return data
    except Exception:
        raise error.ServerError("Error creating payment recipient")


async def update_trans_recipient(
    data_in: schemas.ITransactionRecipientIn, recipient_code: str
):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("transfers_recipient").get("create")}/{recipient_code}',
            json=data_in.dict(),
        )
        data = schemas.TransferRecipientResponse(response.json())
        return data
    except Exception:
        raise error.ServerError("Error updating payment recipient")


async def create_bulk_trans_recipient(
    data_in: t.List[schemas.ITransactionRecipientIn],
):
    try:
        response = await client.request.post(
            url=endpoint.get("transfers_recipient").get("create"),
            json=data_in.dict(),
        )
        data = schemas.TransferRecipientBulkResponse(response.json())
        return data
    except Exception:
        raise error.ServerError("Error creating payment request")


async def get_trans_recipient(recipient_code: str):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("transfers_recipient").get("create")}/{recipient_code}'
        )
        data = schemas.TransferRecipientResponse(response.json())
        return data
    except Exception:
        raise error.ServerError("Error getting payment recipient information")


async def delete_trans_recipient(recipient_code: str):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("transfers_recipient").get("create")}/{recipient_code}'
        )
        data: t.Dict[t.Dict] = response.json()
        return data
    except Exception:
        raise error.ServerError("Error deleting payment recipient")
