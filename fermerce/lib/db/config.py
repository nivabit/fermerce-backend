from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fermerce.core.settings import config


def register_tortoise_to_fastapi(app: FastAPI):
    register_tortoise(
        app,
        db_url=config.get_database_url(),
        modules={"models": ["fermerce.core.model.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
