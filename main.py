from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fermerce.core.settings import config
from fermerce.lib.db.config import register_tortoise_to_fastapi
from fermerce.lib.middleware.response_formatter import response_data_transformer
from fermerce.core.router import v1, admin_v1
from fermerce.core.schemas.response import IHealthCheck
from fermerce.taskiq.broker import broker


def get_application():
    _app = FastAPI(
        title=config.project_name,
        version=config.project_version,
        openapi_url=f"/{config.api_prefix}/v{int(config.project_version)}/openapi.json",
        redoc_url=f"/{config.api_prefix}/v{int(config.project_version)}/redoc",
        contact={
            "email": config.contact_email,
            "name": config.contact_name,
        },
        docs_url=f"/{config.api_prefix}/v{int(config.project_version)}/docs",
        debug=config.debug,
    )
    register_tortoise_to_fastapi(_app)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # _app.middleware("http")(response_data_transformer)

    return _app


app = get_application()


@app.on_event("startup")
async def start_broker():
    if not broker.is_worker_process:
        print("Starting broker")
        await broker.startup()


@app.on_event("shutdown")
async def app_shutdown():
    if not broker.is_worker_process:
        print("Shutting down broker")
        await broker.shutdown()


@app.get("/", response_model=IHealthCheck, tags=["Health status"])
async def health_check():
    return IHealthCheck(
        name=config.project_name,
        version=config.project_version,
        description=config.project_description,
    )


app.include_router(v1.router)
app.include_router(admin_v1.router)
