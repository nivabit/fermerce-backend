import os
import datetime
from typing import List, Optional
from functools import lru_cache
import pydantic as pyd
from fermerce.lib.utils import get_path


class Settings(pyd.BaseSettings):
    # Project base setting details
    debug: bool = os.getenv("DEBUG")
    project_name: str = os.getenv("PROJECT_NAME")
    project_version: float = os.getenv("PROJECT_VERSION")
    project_description: str = os.getenv("PROJECT_DESCRIPTION")
    api_prefix: str = os.getenv("API_PREFIX")
    project_url: str = os.getenv("PROJECT_URL")
    environment: str = os.getenv("ENVIRONMENT")
    backend_cors_origins: List[str] = os.getenv("BACKEND_CORS_ORIGINS")
    app_task_type: str = os.getenv("app_task_type", "direct")
    app_name: str = os.getenv("APP_NAME", "user")

    # admin email settings

    admin_email: str = os.getenv("ADMIN_EMAIL")
    admin_password: str = os.getenv("ADMIN_PASSWORD")
    email_port: int = os.getenv("EMAIL_PORT")
    email_host: str = os.getenv("EMAIL_HOST")
    email_backend: str = os.getenv("EMAIL_BACKEND")
    # developer contact information
    contact_email: str = os.getenv("CONTACT_EMAIL")
    contact_name: str = os.getenv("CONTACT_NAME")
    # Database settings
    db_name: str = os.getenv("DB_NAME")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_port: int = os.getenv("DB_PORT")
    db_host: str = os.getenv("DB_HOST")
    db_type: str = os.getenv("DB_TYPE")

    # background task broker settings e.g rabbit mq, redis etc.
    broker_type: str = os.getenv("BROKER_TYPE")
    broker_host: str = os.getenv("BROKER_HOST")
    broker_port: int = os.getenv("BROKER_PORT")
    broker_user: str = os.getenv("BROKER_USER")
    broker_password: str = os.getenv("BROKER_PASSWORD")
    broker_virtual_host: Optional[str] = os.getenv("BROKER_VIRTUAL_HOST")
    broker_backend_result_url: str = os.getenv("BROKER_BACKEND_RESULT_URL")
    # JSON web token settings
    secret_key: str = os.getenv("SECRET_KEY")
    deta_space_key: str = os.getenv("DETA_SPACE_KEY")
    refresh_secret_key: str = os.getenv("REFRESH_SECRET_KEY")
    upload_key: str = os.getenv("UPLOAD_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_time: int = os.getenv("ACCESS_TOKEN_EXPIRE_TIME")
    refresh_token_expire_time: int = os.getenv("REFRESH_TOKEN_EXPIRE_TIME")
    # payment service settings
    base_payment_url: str = os.getenv("BASE_PAYMENT_URL")
    payment_secret_key: str = os.getenv("PAYMENT_SECRET_KEY")
    payment_public_key: str = os.getenv("PAYMENT_PUBLIC_KEY")
    # project template, static files path settings
    base_dir: pyd.DirectoryPath = get_path.get_base_dir()
    email_template_dir: pyd.DirectoryPath = get_path.get_template_dir()
    static_file_dir: pyd.DirectoryPath = get_path.get_static_file_dir()
    media_url_endpoint_name: str = os.getenv("MEDIA_URL_ENDPOINT_NAME")

    def get_access_expires_time(self):
        return datetime.timedelta(seconds=self.access_token_expire_time)

    def get_refresh_expires_time(
        self,
    ):
        return datetime.timedelta(seconds=self.refresh_token_expire_time)

    def get_database_url(self) -> str:
        if self.environment in [
            "production",
            "development",
            "dev",
        ]:
            return f"{self.db_type}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return f"{self.db_type}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}_test"

    def get_broker_url(self, include_virtue: bool = True) -> str:
        url = f"{self.broker_type}://{self.broker_user}:{self.broker_password}@{self.broker_host}:{self.broker_port}"
        if include_virtue:
            return f"{url}/{self.broker_virtual_host}"
        return url

    def get_broker_result_backend_url(self) -> str:
        return self.broker_backend_result_url

    class Config:
        env_file: str = ".env"


@lru_cache
def get_settings():
    return Settings()


config = get_settings()
