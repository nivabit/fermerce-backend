from esmerald import Request
from edgy import fields

from fermerce.core.model.base_model import BaseModel


class Auth(BaseModel):
    """
    The Auth model
    """

    refresh_token = fields.CharField(max_length=300, null=True)
    access_token = fields.CharField(max_length=300, null=True)
    owner_id = fields.UUIDField(null=True)
    ip_address = fields.CharField(max_length=20, unique=True, null=False, index=True)

    @staticmethod
    def get_user_ip(request: Request) -> str:
        forwarded_for: str = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0]
        elif real_ip:
            client_ip = real_ip
        else:
            client_ip = request.client.host
        return client_ip
