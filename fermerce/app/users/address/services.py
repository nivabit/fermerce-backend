import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.markets.state.models import State
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.users.address import schemas, models


async def create(
    data_in: schemas.IAddressIn,
    user: User,
) -> models.ShippingAddress:
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("shipping state not found")
    check_address = await models.ShippingAddress.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=get_state,
        user=user,
    )
    if check_address:
        raise error.DuplicateError("Address already exists")
    new_address = await models.ShippingAddress.create(
        **data_in.dict(exclude={"state", "phones"}),
        user=user,
        state=get_state,
        phones=",".join(data_in.phones)
    )
    if new_address:
        return new_address
    raise error.ServerError("error creating new shipping address")


async def get(
    address_id: uuid.UUID,
    user: User,
    load_related: bool = False,
) -> models.ShippingAddress:
    query = models.ShippingAddress.filter(id=address_id, user=user)
    result = await filter_and_single(
        model=models.ShippingAddress,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise error.NotFoundError("Shipping address not found")
    return result


async def update(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    user: User,
) -> models.ShippingAddress:
    get_address = await models.ShippingAddress.get_or_none(
        id=address_id, user=user
    ).prefetch_related("state")
    if not get_address:
        raise error.NotFoundError("Address not found")
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("shipping state not found")
    check_if_exist = await models.ShippingAddress.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=get_state,
        user=user,
    )
    if check_if_exist and check_if_exist.id != address_id:
        raise error.DuplicateError("shipping address already exists")
    if get_address.state.id == get_address.id:
        result = await get_address.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                phones=",".join(data_in.phones)
            )
        )
    else:
        result = await get_address.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                state=get_state,
                phones=",".join(data_in.phones)
            )
        )
    try:
        await get_address.save()
        return result
    except:
        raise error.ServerError("Could not update address")


async def filter(
    user: User,
    filter_string: str = "",
    per_page: int = 10,
    page: int = 0,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
) -> t.List[models.ShippingAddress]:
    query = models.ShippingAddress
    if filter_string:
        query = query.filter(
            Q(street__icontains=filter_string)
            | Q(city__icontains=filter_string)
            | Q(state__name__icontains=filter_string)
            | Q(zipcode__icontains=filter_string),
            user=user,
        )

    return await filter_and_list(
        query=query,
        model=models.ShippingAddress,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


async def get_total_count(user: User) -> dict:
    total_add = await models.ShippingAddress.filter(user=user).count()
    return dict(total=len(total_add))


async def delete(
    address_id: uuid.UUID,
    user: User,
) -> Response:
    get_address = await models.ShippingAddress.get_or_none(id=address_id, user=user)
    if not get_address:
        raise error.NotFoundError("Shipping address not found")
    await get_address.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
