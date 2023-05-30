import typing as t
import httpx
from fermerce.core.settings import config

endpoint: t.Dict[str, t.Union[str, t.Dict[str, str]]] = {
    "transfers_recipient": {
        "create": "transferrecipient",
        "bulk_create": "transferrecipient/bulk",
    },
    "transaction": {
        "create": "transaction/initialize",
        "verify": "transaction/verify",
        "authorized_charge": "transaction/charge_authorization",
    },
    "refund": {
        "create": "refund",
        "verify": "transaction/verify",
    },
    "transfer": {
        # use this for creating single or add id_or_transfer_code to get single transfer data,
        "create": "transfer",
        "bulk_create": "transfer/bulk",
        "validate": "transfer/finalize_transfer",
        # add reference id as path parameter,
        "verify": "transfer/verify",
    },
    "bank": {
        "resolve": "bank/resolve",
        "validate": "bank/validate",
    },
}


class Client:
    def __init__(
        self,
        base_url: str = config.base_payment_url,
    ):
        self.base_url = base_url
        self.request = httpx.AsyncClient(base_url=self.base_url)
        self.request.headers.update(
            {
                "Authorization": f"Bearer {config.payment_secret_key}",
                "Content-type": "application/json",
            }
        )


client = Client()
