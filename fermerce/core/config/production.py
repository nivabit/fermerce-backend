import os
import datetime
from typing import List, Optional
from edgy import Registry, Database
from esmerald import CORSConfig, EsmeraldAPISettings, OpenAPIConfig, StaticFilesConfig
from esmerald.config.jwt import JWTConfig
from esmerald.config.template import TemplateConfig
from esmerald.template.jinja import JinjaTemplateEngine
import pydantic as pyd
from fermerce.lib.utils import get_path
from esmerald.openapi.models import Contact
from esmerald.conf.enums import EnvironmentType


class ProductionSettings(EsmeraldAPISettings):
    class Config:
        env_file = ".env"

    # Project base setting details
    environment: str = EnvironmentType.PRODUCTION
    debug: bool = False
    api_prefix: str = "api"
    secret_key: str
    app_name: str = "fermerce"
    project_description: str
    project_url: str
    allow_origins: List[str] = []

    # admin email settings
    smtp_username: str
    smtp_password: str
    smtp_port: int
    smtp_host: str

    # developer contact information
    contact_email: str
    contact_name: str

    # Database settings
    db_name: str
    db_user: str
    db_password: str
    db_port: int
    db_host: str
    db_driver: str

    # background task broker settings e.g rabbit mq, redis etc.
    broker_type: str
    broker_host: str
    broker_port: int
    broker_user: str
    broker_password: str
    broker_virtual_host: Optional[str]
    broker_backend_result_url: str

    # Google API Key
    google_api_key: str
    # payment service settings
    base_payment_url: str
    payment_secret_key: str
    payment_public_key: str
    # project template, static files path settings
    base_dir: pyd.DirectoryPath = get_path.get_base_dir()
    media_url_endpoint_name: str = "medias"
    email_template_dir: pyd.DirectoryPath = get_path.get_template_dir()
    static_file_dir: pyd.DirectoryPath = get_path.get_static_file_dir()

    @property
    def password_hashers(self) -> List[str]:
        return [
            "esmerald.contrib.auth.hashers.PBKDF2PasswordHasher",
            "esmerald.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        ]

    @property
    def cors_config(self) -> CORSConfig:
        if not self.allow_origins:
            return None
        return CORSConfig(
            allow_origins=self.allow_origins,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
            allow_credentials=True,
        )

    @property
    def openapi_config(self) -> OpenAPIConfig:
        """
        Override the default openapi_config from Esmerald.
        """
        return OpenAPIConfig(
            title=self.app_name,
            docs_url="/swagger",
            redoc_url="/redoc",
            stoplight_url="/stoplight",
            contact=Contact(name=self.contact_name, email=self.contact_email),
            description=self.project_description,
        )

    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            directory=get_path.get_template_dir(),
            engine=JinjaTemplateEngine,
        )

    @property
    def jwt_config(self) -> JWTConfig:
        return JWTConfig(
            signing_key=self.secret_key,
            auth_header_types=["Bearer", "Token"],
            refresh_token_lifetime=datetime.timedelta(minutes=30),
            access_token_lifetime=datetime.timedelta(days=1),
            user_id_field="id",
            user_id_claim="user_id",
            refresh_token_name="refresh_token",
            access_token_name="access_token",
        )

    @property
    def static_files_config(self) -> StaticFilesConfig:
        return StaticFilesConfig(
            path="/static",
            directory=get_path.get_static_file_dir(),
        )

    @property
    def database_config(self) -> tuple[Database, Registry]:
        database = Database(self.get_database_url())
        return database, Registry(database=database)

    def get_database_url(self) -> str:
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def get_broker_url(self, include_virtue: bool = True) -> str:
        url = f"{self.broker_type}://{self.broker_user}:{self.broker_password}@{self.broker_host}:{self.broker_port}"
        if include_virtue:
            return f"{url}/{self.broker_virtual_host}"
        return url

    def get_broker_result_backend_url(self) -> str:
        return self.broker_backend_result_url
