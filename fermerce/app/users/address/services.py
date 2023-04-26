import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.markets.state.models import State
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder
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
        **data_in.dict(exclude={"state"}), user=user, state=get_state
    )
    if new_address:
        return new_address
    raise error.ServerError("error creating new shipping address")


async def get(
    address_id: uuid.UUID,
    user: User,
) -> models.ShippingAddress:
    get_address = await models.ShippingAddress.get_or_none(
        id=address_id, user=user
    ).prefetch_related("state")
    if not get_address:
        raise error.NotFoundError("Shipping address not found")
    return get_address


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
        result = await get_address.update_from_dict(dict(**data_in.dict(exclude="state")))
    else:
        result = await get_address.update_from_dict(
            dict(**data_in.dict(exclude="state"), state=get_state)
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

    to_order_by = []
    if sort_by == SortOrder.asc and order_by:
        for el in order_by.split(","):
            if hasattr(models.ShippingAddress, el):
                to_order_by.append(f"-{el}")
    elif sort_by == SortOrder.desc and order_by:
        for el in order_by.split(","):
            if hasattr(models.ShippingAddress, el):
                to_order_by.append(el)
    query = query.order_by(*to_order_by).prefetch_related("state")
    offset = (page - 1) * per_page
    limit = per_page
    results = await query.limit(limit).offset(offset).all()
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


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
    await get_address.delete(address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
