import typing as t
from uuid_extensions import uuid7str
from esmerald import Request, UploadFile
from edgy import fields
from fermerce.core.model.base_model import BaseModel
from fermerce.core.settings import config


class Media(BaseModel):
    url = fields.CharField(max_length=300, unique=True)
    content_type = fields.CharField(max_length=30)
    alt = fields.CharField(max_length=50, unique=True)

    @classmethod
    def allowed_image_extensions(cls) -> list[str]:
        return ["jpg", "png", "jpeg", "gif", "webp"]

    @staticmethod
    def allowed_document_extensions() -> list[str]:
        return ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"]

    @staticmethod
    def allowed_video_extensions() -> list[str]:
        return ["mp4", "mov", "avi", "wmv", "mkv"]

    @staticmethod
    def allowed_audio_extensions() -> list[str]:
        return ["mp3", "ogg", "wav"]

    @classmethod
    def all_allowed_files(cls) -> list[str]:
        return [
            *cls.allowed_image_extensions(),
            *cls.allowed_document_extensions(),
            *cls.allowed_video_extensions(),
            *cls.allowed_audio_extensions(),
        ]

    @staticmethod
    def convert_image_name_to_url(media_url: str, request: Request) -> str:
        image_full_url = (
            f"{request.url_for(config.media_url_endpoint_name, uri=media_url)}"
        )
        return image_full_url

    @staticmethod
    def check_file_type(
        file_type: t.Union[list[str], str] = None,
        media_objs: list[UploadFile] = [],
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
    def generate_unique_name(file: UploadFile, desired_file_type: str = None):
        """Generate a unique name for a file"""
        extension = (
            file.content_type.split("/")[-1]
            if not desired_file_type
            else desired_file_type
        )
        unique_filename = f"{uuid7str()}.{extension}"
        return unique_filename

    def get_file_type(self, content_type: str, to_check: str):
        return content_type.lower().endswith("/" + to_check.lower())
