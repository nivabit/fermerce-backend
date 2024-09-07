import edgy
from uuid_extensions import uuid7str
from fermerce.core.settings import config

_, registry = config.database_config


class BaseModel(edgy.Model):
    id = edgy.UUIDField(primary_key=True, default=uuid7str)
    created_at = edgy.DateTimeField(auto_now_add=True)
    updated_at = edgy.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        registry = registry

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.Meta.abstract:
            cls.Meta.tablename = f"fm_{cls.__name__.lower()}"
