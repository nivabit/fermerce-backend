import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.state.models import State
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.warehouse import schemas, models


async def create_warehouse(data_in: schemas.IWarehouseIn):
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("state not found")
    check_warehouse = await models.WereHouse.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=get_state,
    )
    if check_warehouse:
        raise error.DuplicateError("warehouse already exists")
    new_warehouse = await models.WereHouse.create(
        **data_in.dict(exclude={"state", "phones"}),
        state=get_state,
        phones=",".join(data_in.phones),
    )
    if new_warehouse:
        return new_warehouse
    raise error.ServerError("error creating warehouse")


async def get_warehouse(
    warehouse_id: uuid.UUID,
    load_related: bool = False,
) -> models.WereHouse:
    query = models.WereHouse.filter(id=warehouse_id)
    result = await filter_and_single(
        model=models.WereHouse,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise error.NotFoundError("address not found")
    return result


async def update_warehouse(
    warehouse_id: uuid.UUID,
    data_in: schemas.IWarehouseIn,
) -> models.WereHouse:
    get_warehouse = await models.WereHouse.get_or_none(
        id=warehouse_id,
    ).prefetch_related(
        "state",
    )
    if not get_warehouse:
        raise error.NotFoundError("warehouse not found")
    state = get_warehouse.state
    if state.id != data_in.state:
        state = await State.get_or_none(id=data_in.state)
    if not state:
        raise error.NotFoundError("state not found")

    check_if_exist = await models.WereHouse.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=state,
    )
    if check_if_exist:
        raise error.DuplicateError("warehouse already exists")
    if state.id == get_warehouse.state.id:
        result = await get_warehouse.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                phones=",".join(data_in.phones),
            )
        )
    else:
        result = await get_warehouse.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                state=state,
                phones=",".join(data_in.phones),
            )
        )

    if check_if_exist:
        await get_warehouse.save()
        return result
    raise error.ServerError("Could not update warehouse ")


async def warehouse_filter(
    filter_string: str = "",
    per_page: int = 10,
    page: int = 0,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
) -> t.List[models.WereHouse]:
    query = models.WereHouse
    if filter_string:
        query = query.filter(
            Q(street__icontains=filter_string)
            | Q(city__icontains=filter_string)
            | Q(state__name__icontains=filter_string)
            | Q(zipcode__icontains=filter_string),
        )

    return await filter_and_list(
        query=query,
        model=models.WereHouse,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


async def delete_warehouse(warehouse_id: uuid.UUID) -> Response:
    get_warehouse = await models.WereHouse.get_or_none(id=warehouse_id)
    if not get_warehouse:
        raise error.NotFoundError("warehouse not found")
    await get_warehouse.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
