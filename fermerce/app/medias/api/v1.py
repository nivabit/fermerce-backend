import typing as t
from fastapi import APIRouter, Depends, Form, Header, Request, UploadFile
from fastapi.responses import StreamingResponse
from fermerce.app.medias import schemas, services
from fermerce.core.settings import config
from fermerce.app.user.dependency import require_user
from fermerce.lib.shared.dependency import AppAuth

router = APIRouter(
    prefix="/static",
    tags=["static"],
)


@router.post(
    "/",
    dependencies=[
        # Depends(AppAuth.verify_file_upload_api_key),
    ],
)
async def create_resource(
    request: Request,
    files: t.List[UploadFile] = Form(media_type="multipart/form-data"),
):
    return await services.create(
        request=request,
        media_objs=files,
    )


@router.put("/{uri}", dependencies=[Depends(require_user)])
async def update_resource(uri: str, file: UploadFile = Form()):
    return await services.update(uri=uri, media_obj=file)


@router.get("/{uri}", name=config.media_url_endpoint_name)
async def get_resource(uri: str) -> StreamingResponse:
    return await services.get(uri)


@router.get(
    "/{uri}/download",
    dependencies=[
        Depends(require_user),
        Depends(AppAuth.verify_file_upload_api_key),
    ],
)
async def download_resource(uri: str) -> StreamingResponse:
    return await services.download(uri)


@router.delete(
    "/{uri}",
    dependencies=[
        Depends(require_user),
        Depends(AppAuth.verify_file_upload_api_key),
    ],
)
async def delete_one_resource(uri: str) -> None:
    return await services.delete_one(uri)


@router.delete(
    "/",
    dependencies=[
        Depends(require_user),
        Depends(AppAuth.verify_file_upload_api_key),
    ],
)
async def delete_many_resource(data_in: schemas.IMediaDeleteIn) -> None:
    return await services.delete_many(data_in)
