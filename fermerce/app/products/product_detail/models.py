from tortoise import fields, models


class ProductDetail(models.Model):
    class Meta:
        table = "product_detail"

    id = fields.UUIDField(pk=True, index=True)
    title = fields.CharField(max_length=50, null=False)
    description = fields.TextField(null=False)
    product = fields.ForeignKeyField("models.Product", related_name="details")

    class Meta:
        table = "fm_product_detail"
