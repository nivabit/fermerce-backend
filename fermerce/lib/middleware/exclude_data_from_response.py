import json
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, List
from fastapi.concurrency import iterate_in_threadpool


def remove_exclude_from_list(exclude_list: list[str], data: list):
    for key in exclude_list:
        try:
            data.remove(key)
        except ValueError:
            pass
    return data


def remove_exclude_from_dict(exclude_list: dict[str], data: dict):
    for key in exclude_list:
        data.pop(key, None)
    return data


async def pop_exclude(response_body, exclude_keys: List[str]) -> None:
    data = json.loads(response_body)
    if isinstance(data, list):
        data = remove_exclude_from_list(exclude_list=exclude_keys, data=data)
        for item in data:
            if isinstance(item, dict):
                item = remove_exclude_from_dict(exclude_list=exclude_keys, data=item)
                for _, value in item.items():
                    if isinstance(value, list):
                        value = remove_exclude_from_list(exclude_list=exclude_keys, data=value)
                    elif isinstance(value, dict):
                        value = remove_exclude_from_dict(exclude_list=exclude_keys, data=value)
    elif isinstance(data, dict):
        data = remove_exclude_from_dict(exclude_list=exclude_keys, data=data)
        for _, value in data.items():
            if isinstance(value, list):
                value = remove_exclude_from_list(exclude_list=exclude_keys, data=data)
            elif isinstance(value, dict):
                value = remove_exclude_from_dict(exclude_list=exclude_keys, data=value)
    return data


def exclude_keys_middleware(exclude_keys: List[str] = None) -> Any:
    if not exclude_keys:
        exclude_keys = []

    async def middleware(request: Request, call_next):
        response = await call_next(request)
        try:
            content_type = response.headers.get("content-type", "")
            if (
                "application/json" in content_type
                and response.status_code <= status.HTTP_226_IM_USED
            ):
                response_body = [chunk async for chunk in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(iter(response_body))
                response_data = await pop_exclude(
                    response_body[0].decode(), exclude_keys=exclude_keys
                )
                return JSONResponse(
                    status_code=response.status_code,
                    content=response_data,
                    media_type=response.media_type,
                )
            return response
        except Exception:
            return response

    return middleware
