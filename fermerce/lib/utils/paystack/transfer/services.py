import typing as t
from fermerce.lib.utils.paystack.transfer import schemas
from fermerce.lib.utils.paystack import client, endpoint
from fermerce.lib.errors import error


# Create Transfers
async def create_transfer(data_in: schemas.ITransferDataIn):
    try:
        response = await client.request.post(
            url=endpoint.get("transfer").get("create"), json=data_in.dict()
        )
        data: schemas.ICreateTransferResponse = response.json()
        return data
    except Exception:
        raise error.ServerError("Error creating transfer")


async def finalize_transfer(data_in: schemas.ITransferValidatedIn):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("transfer").get("validate")}',
            json=data_in.dict(),
        )
        data: schemas.ICreateTransferResponse = response.json()
        return data
    except Exception:
        raise error.ServerError("Error validating transfer")


async def create_bulk_transfer(data_in: t.List[t.List[schemas.ITransferDataIn]]):
    try:
        response = await client.request.post(
            url=endpoint.get("transfer").get("bulk"), json=data_in.dict()
        )
        data: schemas.ICreateTransferListResponse = response.json()
        return data
    except Exception:
        raise error.ServerError("Error creating bulk transfer")


async def list_transfer():
    try:
        response = await client.request.post(url=endpoint.get("transfer").get("create"))
        data: schemas.ITransferListResponse = response.json()
        return data
    except Exception:
        raise error.ServerError("Error listing payment recipient")


async def get_transfer(transfer_code: str):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("transfers_recipient").get("create")}/{transfer_code}'
        )
        data: schemas.ICreateTransferResponse = response.json()
        return data
    except Exception:
        raise error.ServerError("Error getting payment recipient information")


async def verify_transfer(transfer_code: str):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("transfer").get("verify")}/{transfer_code}'
        )
        data = schemas.ICreateTransferResponse(**response.json())
        return data
    except Exception:
        raise error.ServerError("Error deleting payment recipient")
