from edgy import fields

from fermerce.core.model.base_model import BaseModel


class Review(BaseModel):
    comment = fields.CharField(max_length=500, null=True)
    rating = fields.FloatField(default=0.0, null=True)
    reviewed = fields.BooleanField(default=False, null=True)
    user = fields.ForeignKey("User", related_name="reviews")
    medias = fields.ManyToManyField("Media", through="fm_media")
    product = fields.ForeignKey("Product", related_name="reviews")
