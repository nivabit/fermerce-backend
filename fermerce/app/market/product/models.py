from uuid_extensions import uuid7str
from edgy import fields
from fermerce.app.vendor.models import Vendor
from fermerce.core.model.base_model import BaseModel
from fermerce.lib.utils.random_string import random_str


class Product(BaseModel):
    name = fields.CharField(max_length=50, null=False)
    slug = fields.CharField(max_length=150, null=False)
    description = fields.TextField(null=False)
    in_stock = fields.BooleanField(default=False)
    is_suspended = fields.BooleanField(default=False)
    sku = fields.CharField(
        max_length=25,
        default=f"PR-{uuid7str()[:10]}",
        unique=True,
    )
    cover_media = fields.ForeignKey(
        "Media",
        related_name="cover_media",
        null=True,
    )
    galleries = fields.ManyToManyField(
        "Media",
        related_name="product_galleries",
        through="fm_product_media_gallery",
    )
    categories = fields.ManyToManyField(
        "ProductCategory",
        related_name="products",
        through="fm_product_rel_category",
    )
    vendor: Vendor | None = fields.ForeignKey(
        "Vendor",
        related_name="products",
    )

    @staticmethod
    def make_slug(name: str, random_length: int = 10) -> str:
        slug = f"{name.replace(' ', '-').replace('_', '-')[:30]}-{random_str(random_length).strip().lower()}"
        return slug
