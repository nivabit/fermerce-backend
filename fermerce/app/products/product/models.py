import uuid
from tortoise import fields, models
from fermerce.app.business.vendor.models import Vendor
from fermerce.app.products.category.models import ProductCategory
from fermerce.app.products.selling_units.models import ProductSellingUnit
from fermerce.app.products.promo_code.models import ProductPromoCode


from fermerce.lib.utils.random_string import random_str


class ProductDetail(models.Model):
    class Meta:
        table = "product_detail"

    id = fields.UUIDField(pk=True, index=True)
    title = fields.CharField(max_length=50, null=False)
    description = fields.TextField(null=False)
    product = fields.ForeignKeyField("models.Product", related_name="details")


class Product(models.Model):
    class Meta:
        table = "product"
        ordering = ["-id", "-created_at"]

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=50, null=False)
    slug = fields.CharField(max_length=70, null=False)
    description = fields.TextField(null=False)
    in_stock = fields.BooleanField(default=False)
    is_suspended = fields.BooleanField(default=False)
    sku = fields.CharField(
        max_length=25,
        default=f"PR-{str(uuid.uuid4()).split('-')[-1]}",
        unique=True,
    )
    cover_media = fields.ForeignKeyField("models.Media", related_name="cover_media", null=True)
    galleries = fields.ManyToManyField(
        "models.Media",
        related_name="product_galleries",
    )
    categories: fields.ManyToManyRelation[ProductCategory] = fields.ManyToManyField(
        "models.ProductCategory", related_name="products"
    )
    measurement_units: fields.ForeignKeyRelation[ProductSellingUnit]
    promo_codes: fields.ManyToManyRelation[ProductPromoCode]
    details: fields.ForeignKeyNullableRelation[ProductDetail]
    vendor: fields.ForeignKeyRelation[Vendor] = fields.ForeignKeyField(
        "models.Vendor", related_name="products"
    )
    created_at = fields.DatetimeField(auto_now=True)
    modified_at = fields.DatetimeField(auto_now_add=True)

    @staticmethod
    def make_slug(name: str, random_length: int = 10) -> str:
        slug = f"{name.replace(' ', '-').replace('_', '-')[:30]}-{random_str(random_length).strip().lower()}"
        return slug
