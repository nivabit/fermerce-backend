from fermerce.lib.paystack.refund import schemas
from fermerce.lib.paystack import client, endpoint
from fermerce.lib.errors import error


# payment refund
async def create_refund(data_in: schemas.RefundTransactionIn):
    try:
        response = await client.request.post(
            url=endpoint.get("refund").get("create"), json=data_in.dict()
        )
        data: schemas.IRefundSingleResponse = response.json()
        return data
    except Exception:
        raise error.BadDataError(detail="Error refunding transaction")


async def get_refund(reference_code: str):
    try:
        response = await client.request.post(
            url=f'{endpoint.get("refund").get("create")}/{reference_code}'
        )
        data: schemas.IRefundSingleResponse = response.json()
        return data
    except Exception:
        raise error.ServerError("Error listing refunds")
