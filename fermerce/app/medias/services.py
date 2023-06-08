import typing as t
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.errors import error
from fastapi import Request, UploadFile, status
from fastapi.responses import StreamingResponse
from fermerce.app.medias import models, schemas, utils
from fermerce.app.medias.drives import product_drive


async def create(
    request: Request,
    media_objs: t.Optional[t.List[UploadFile]],
    desire_alt: str = None,
):
    try:
        bad_types = models.Media.check_file_type(
            file_type=models.Media.all_allowed_files(), media_objs=media_objs
        )
        if bad_types:
            raise error.BadDataError("Unsupported media type, expected")
        to_out = []
        for media in media_objs:
            file_bytes, content_type = await utils.compress_file(media)
            file_name = models.Media.generate_unique_name(
                media, desired_file_type=content_type.split("/")[1]
            )
            result = product_drive.put(
                name=file_name, data=file_bytes, content_type=content_type
            )
            if result is not None:
                get_url = models.Media.convert_image_name_to_url(
                    media_url=result, request=request
                )
                result = await models.Media.create(
                    url=get_url,
                    content_type=content_type,
                    alt=desire_alt if desire_alt else file_name,
                )
                to_out.append(result)
        return to_out

    except Exception as e:
        raise error.ServerError("Error while creating resource" + str(e))


async def update(uri: str, media_obj: UploadFile) -> IResponseMessage:
    try:
        get_media = await models.Media.get_or_none(alt=uri)
        if not get_media:
            raise error.NotFoundError(f"Resource with URI {uri} not found")
        bad_types = models.Media.check_file_type(
            file_type=models.Media.all_allowed_files, media_objs=[media_obj]
        )
        if bad_types:
            raise error.BadDataError("Unsupported media type")
        expected_extension = get_media.content_type.split("/")[0]
        actual_extension = media_obj.content_type.split("/")[0]
        if expected_extension != actual_extension:
            raise error.BadDataError(
                f"Invalid file extension. Expected {expected_extension} but got {actual_extension}."
            )
        file_bytes = utils.compress_file(file=media_obj)
        if file_bytes:
            product_drive.put(name=uri, data=file_bytes)
            return IResponseMessage(message="Resource updated successfully")
    except Exception:
        raise error.ServerError(
            f"Error while updating resource with URI {uri}. Make sure you are uploading a valid file."
        )


async def get(uri: str) -> StreamingResponse:
    check_file = product_drive.get(uri)
    if not check_file:
        raise error.NotFoundError("Resource Not found")
    return StreamingResponse(
        content=check_file.iter_chunks(chunk_size=1024),
        status_code=status.HTTP_200_OK,
    )


async def download(
    uri: str,
) -> StreamingResponse:
    check_file = product_drive.get(uri)
    if not check_file:
        raise error.NotFoundError("Resource Not found")
    headers = {
        "Content-Disposition": f"attachment; filename={uri}",
    }
    return StreamingResponse(
        check_file.iter_chunks(chunk_size=1024),
        headers=headers,
        status_code=status.HTTP_200_OK,
    )


async def delete_many(data_in: schemas.IMediaDeleteIn) -> IResponseMessage:
    check_file = await models.Media.filter(url__in=data_in.uris).delete()
    if check_file:
        product_drive.delete_many(data_in.uris)
        return IResponseMessage(message="Resource deleted successfully")
    raise error.NotFoundError("Resource Not found")


async def delete_one(uri: str) -> IResponseMessage:
    check_file = await models.Media.get_or_none(alt=uri)
    if check_file:
        await check_file.delete()
        product_drive.delete(uri)
        return IResponseMessage(message="Resource deleted successfully")
    raise error.NotFoundError("Resource Not found")
