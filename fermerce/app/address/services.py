import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.state.models import State
from fermerce.app.user.models import User
from fermerce.app.vendor.models import Vendor
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.address import schemas, models


async def user_create(data_in: schemas.IAddressIn, user: User) -> models.Address:
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("shipping state not found")

    check_address = await models.Address.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=get_state,
        users=user,
    )
    if check_address:
        raise error.DuplicateError("shipping address already exists")
    new_address = await models.Address.create(
        **data_in.dict(exclude={"state", "phones"}),
        state=get_state,
        phones=",".join(data_in.phones),
    )

    if new_address:
        await user.shipping_address.add(new_address)
        return new_address
    raise error.ServerError("error creating address")


async def vendor_create(data_in: schemas.IAddressIn, vendor: Vendor):
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("state not found")
    check_address = await models.Address.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=get_state,
        vendors=vendor,
    )
    if check_address:
        raise error.DuplicateError("business address already exists")
    new_address = await models.Address.create(
        **data_in.dict(exclude={"state", "phones"}),
        state=get_state,
        phones=",".join(data_in.phones),
    )
    if new_address:
        await vendor.address.add(new_address)
        return new_address
    raise error.ServerError("error creating address")


async def user_get(
    address_id: uuid.UUID,
    user: User,
    load_related: bool = False,
) -> models.Address:
    query = models.Address.filter(id=address_id, users=user)
    result = await filter_and_single(
        model=models.Address,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise error.NotFoundError("address not found")
    return result


async def vendor_get(
    address_id: uuid.UUID,
    vendor: Vendor,
    load_related: bool = False,
) -> models.Address:
    query = models.Address.filter(id=address_id).filter(vendors__in=[vendor])
    result = await filter_and_single(
        model=models.Address,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise error.NotFoundError("address not found")
    return result


async def user_update(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    user: User,
) -> models.Address:
    get_address = await models.Address.get_or_none(
        id=address_id,
        users=user,
    ).prefetch_related("state")
    if not get_address:
        raise error.NotFoundError("Address not found")
    state = get_address.state
    if state.id != data_in.state:
        state = await State.get_or_none(id=data_in.state)
    if not state:
        raise error.NotFoundError("shipping state not found")

    check_if_exist = await models.Address.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=state,
        users=user,
    )
    if check_if_exist:
        raise error.DuplicateError("shipping address already exists")
    if state.id == get_address.state.id:
        get_address.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                phones=",".join(data_in.phones),
            )
        )
    else:
        get_address.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                state=state,
                phones=",".join(data_in.phones),
            )
        )

    if get_address:
        await get_address.save()
        return get_address
    raise error.ServerError("Could not update address")


async def vendor_update(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    vendor: Vendor,
) -> models.Address:
    get_address = await models.Address.get_or_none(
        id=address_id, vendors__in=[vendor]
    ).prefetch_related("state")
    if not get_address:
        raise error.NotFoundError("Address not found")
    state = get_address.state
    if state.id != data_in.state:
        state = await State.get_or_none(id=data_in.state)
    if not state:
        raise error.NotFoundError("state not found")

    check_if_exist = await models.Address.get_or_none(
        street=data_in.street,
        city=data_in.city,
        zipcode=data_in.zipcode,
        state=state,
        vendors__in=[vendor],
    )
    if check_if_exist:
        raise error.DuplicateError("address already exists")
    if state.id == get_address.state.id:
        result = await get_address.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                phones=",".join(data_in.phones),
            )
        )
    else:
        result = await get_address.update_from_dict(
            dict(
                **data_in.dict(exclude={"state", "phones"}),
                state=state,
                phones=",".join(data_in.phones),
            )
        )

    if check_if_exist:
        await get_address.save()
        return result
    raise error.ServerError("Could not update address")


async def user_filter(
    user: User,
    filter_string: str = "",
    per_page: int = 10,
    page: int = 0,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
) -> t.List[models.Address]:
    query = models.Address
    if filter_string:
        query = query.filter(
            Q(street__icontains=filter_string)
            | Q(city__icontains=filter_string)
            | Q(state__name__icontains=filter_string)
            | Q(zipcode__icontains=filter_string),
        )

    query = query.filter(users=user)
    return await filter_and_list(
        query=query,
        model=models.Address,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


async def vendor_filter(
    vendor: Vendor,
    filter_string: str = "",
    per_page: int = 10,
    page: int = 0,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    load_related: bool = False,
) -> t.List[models.Address]:
    query = models.Address
    if filter_string:
        query = query.filter(
            Q(street__icontains=filter_string)
            | Q(city__icontains=filter_string)
            | Q(state__name__icontains=filter_string)
            | Q(zipcode__icontains=filter_string),
        )

    query = query.filter(vendors__in=[vendor])
    return await filter_and_list(
        query=query,
        model=models.Address,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


async def user_delete(
    address_id: uuid.UUID,
    user: User,
) -> Response:
    get_address = None

    get_address = await models.Address.get_or_none(id=address_id, users__in=[user])
    if not get_address:
        raise error.NotFoundError("Shipping address not found")
    await get_address.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def vendor_delete(
    address_id: uuid.UUID,
    vendor: Vendor,
) -> Response:
    get_address = await models.Address.get_or_none(id=address_id, vendors__in=[vendor])
    if not get_address:
        raise error.NotFoundError("address not found")
    await get_address.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
