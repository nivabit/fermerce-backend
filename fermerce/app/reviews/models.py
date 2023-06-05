import uuid
from tortoise import fields, models


class Review(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    comment = fields.CharField(max_length=500, null=True)
    rating = fields.FloatField(default=0.0, null=True)
    reviewed = fields.BooleanField(default=False, null=True)
    user = fields.ForeignKeyField("models.User", related_name="reviews")
    medias = fields.ManyToManyField("models.Media", through="fm_media")
    product = fields.ForeignKeyField("models.Product", related_name="reviews")
    created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_order_review"
