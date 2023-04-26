import typing as t
from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.concurrency import iterate_in_threadpool


async def transform(s: t.Union[str, bytearray, bytes], status_code: int):
    import json

    response_data = dict(status=status_code, data=None, error=None)
    if status_code <= status.HTTP_226_IM_USED:
        try:
            data: dict = json.loads(s)
            if isinstance(data, dict) and len(list(data.keys())) == 1:
                response_data["data"] = data
                # response_data["data"] = ",".join(list(data.values()))
            else:
                response_data["data"] = data
        except Exception:
            response_data["data"] = s
            return response_data
        finally:
            return response_data

    if status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        try:
            data: dict = json.loads(s)
            response_data["error"] = {k.get("loc")[-1]: k.get("msg") for k in data["detail"]}
        except Exception:
            response_data["error"] = s
        finally:
            return response_data
    if status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        response_data["error"] = "Internal Server Error, please try again"
        return response_data
    if status_code >= status.HTTP_400_BAD_REQUEST:
        try:
            data: dict = json.loads(s)
            if len(list(data.keys())) == 1:
                response_data["error"] = ",".join(list(data.values()))
        except Exception:
            response_data["error"] = s
        finally:
            return response_data
    return response_data


async def response_data_transformer(request: Request, call_next):
    response: Response = await call_next(request)
    try:
        content_type: str = str(response.headers.get("content-type", None)).lower()
        exclude_url: str = str(request.url).split("/")[-1].lower()
        if content_type.split(";")[0] == "text/html" or exclude_url == "openapi.json":
            return response
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        data = await transform(
            s=response_body[0].decode(),
            status_code=response.status_code,
        )

        return JSONResponse(
            status_code=response.status_code,
            content=data,
            media_type=response.media_type,
        )

    except Exception:
        return response
