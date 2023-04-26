import uuid
import typing as t
from fastapi import Request, UploadFile
from tortoise import fields, models
from fermerce.app.products.product.models import Product
from fermerce.core.settings import config


class Media(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    url = fields.CharField(max_length=300, unique=True)
    uri = fields.CharField(max_length=50, unique=True)

    @property
    def allowed_image_extensions(self) -> t.List[str]:
        return ["jpg", "png", "jpeg", "gif", "webp"]

    @property
    def allowed_document_extensions(self) -> t.List[str]:
        return ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"]

    @property
    def allowed_video_extensions(self) -> t.List[str]:
        return ["mp4", "mov", "avi", "wmv", "mkv"]

    @property
    def allowed_audio_extensions(self) -> t.List[str]:
        return ["mp3", "ogg", "wav"]

    @property
    def all_allowed_files(self) -> t.List[str]:
        return [
            *self.allowed_image_extensions,
            *self.allowed_document_extensions,
            *self.allowed_video_extensions,
            *self.allowed_audio_extensions,
        ]

    @staticmethod
    def convert_image_name_to_url(media_url: str, request: Request) -> str:
        image_full_url = f"{request.url_for(config.media_url_endpoint_name, uri=media_url)}"
        return image_full_url

    def check_file_type(
        self,
        file_type: t.Union[t.List[str], str] = None,
        media_objs: t.List[UploadFile] = [],
    ) -> bool:
        if not media_objs:
            return False
        if not file_type:
            raise ValueError("file_type cannot be empty")
        not_allowed_file_types = [
            media.filename.split(".")[-1]
            for media in media_objs
            if media.content_type.split("/")[-1] not in file_type
        ]
        return bool(not_allowed_file_types)

    @staticmethod
    def generate_unique_name(file: UploadFile):
        """Generate a unique name for a file"""
        extension = file.content_type.split("/")[-1]
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        return unique_filename

    def get_file_type(self, content_type: str, to_check: str):
        return content_type.lower().endswith("/" + to_check.lower())
