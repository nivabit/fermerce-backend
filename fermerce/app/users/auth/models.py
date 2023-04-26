import uuid
from fastapi import Request
from tortoise import fields, models


class Auth(models.Model):
    """
    The Auth model
    """

    id = fields.UUIDField(pk=True, default=uuid.uuid4())
    refresh_token = fields.CharField(max_length=300, null=True)
    access_token = fields.CharField(max_length=300, null=True)
    user = fields.ForeignKeyField(
        "models.User", related_name="auths", on_delete=fields.CASCADE
    )
    ip_address = fields.CharField(max_length=20, unique=True, null=False, index=True)

    @staticmethod
    def get_user_ip(request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0]
        elif real_ip:
            client_ip = real_ip
        else:
            client_ip = request.client.host
        return client_ip
