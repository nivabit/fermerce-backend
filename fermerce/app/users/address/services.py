import uuid
import typing as t
from esmerald import status, Response, AsyncDAOProtocol
from edgy import Q
from fermerce.app.state.models import State
from fermerce.app.user.models import User
from fermerce.app.vendor.models import Vendor
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base_old import (
    BaseRepository,
    filter_and_list,
    filter_and_single,
)
from fermerce.lib.exceptions import exceptions
from fermerce.app.address import schemas, models


class AddressDAO(AsyncDAOProtocol):
    async def user_create(
        self, payload: schemas.IAddressIn, user: User
    ) -> models.Address:
        get_state = await State.query.get_or_none(id=payload.state)
        if not get_state:
            raise exceptions.NotFoundError("shipping state not found")

        check_address = await models.Address.query.filter(
            street=payload.street,
            city=payload.city,
            zipcode=payload.zipcode,
            state=get_state,
            users=user,
        ).first()
        if check_address:
            raise exceptions.DuplicateError("shipping address already exists")
        new_address = await models.Address.query.create(
            **payload.model_dump(exclude={"state", "phones"}),
            state=get_state,
            phones=",".join(payload.phones),
        )

        if new_address:
            await user.shipping_address.add(new_address)
            return new_address
        raise exceptions.ServerError("error creating address")


async def vendor_create(payload: schemas.IAddressIn, vendor: Vendor):
    get_state = await State.get_or_none(id=payload.state)
    if not get_state:
        raise exceptions.NotFoundError("state not found")
    check_address = await models.Address.query.filter(
        street=payload.street,
        city=payload.city,
        zipcode=payload.zipcode,
        state=get_state,
        vendors=vendor,
    ).first()
    if check_address:
        raise exceptions.DuplicateError("business address already exists")
    new_address = await models.Address.create(
        **payload.model_dump(exclude={"state", "phones"}),
        state=get_state,
        phones=",".join(payload.phones),
    )
    if new_address:
        await vendor.address.add(new_address)
        return new_address
    raise exceptions.ServerError("error creating address")


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
        raise exceptions.NotFoundError("address not found")
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
        raise exceptions.NotFoundError("address not found")
    return result


async def user_update(
    address_id: uuid.UUID,
    payload: schemas.IAddressIn,
    user: User,
) -> models.Address:
    get_address = await models.Address.get_or_none(
        id=address_id,
        users=user,
    ).prefetch_related("state")
    if not get_address:
        raise exceptions.NotFoundError("Address not found")
    state = get_address.state
    if state.id != payload.state:
        state = await State.get_or_none(id=payload.state)
    if not state:
        raise exceptions.NotFoundError("shipping state not found")

    check_if_exist = await models.Address.get_or_none(
        street=payload.street,
        city=payload.city,
        zipcode=payload.zipcode,
        state=state,
        users=user,
    )
    if check_if_exist:
        raise exceptions.DuplicateError("shipping address already exists")
    if state.id == get_address.state.id:
        get_address.update_from_dict(
            dict(
                **payload.dict(exclude={"state", "phones"}),
                phones=",".join(payload.phones),
            )
        )
    else:
        get_address.update_from_dict(
            dict(
                **payload.dict(exclude={"state", "phones"}),
                state=state,
                phones=",".join(payload.phones),
            )
        )

    if get_address:
        await get_address.save()
        return get_address
    raise exceptions.ServerError("Could not update address")


async def vendor_update(
    address_id: uuid.UUID,
    payload: schemas.IAddressIn,
    vendor: Vendor,
) -> models.Address:
    get_address = await models.Address.get_or_none(
        id=address_id, vendors__in=[vendor]
    ).prefetch_related("state")
    if not get_address:
        raise exceptions.NotFoundError("Address not found")
    state = get_address.state
    if state.id != payload.state:
        state = await State.get_or_none(id=payload.state)
    if not state:
        raise exceptions.NotFoundError("state not found")

    check_if_exist = await models.Address.get_or_none(
        street=payload.street,
        city=payload.city,
        zipcode=payload.zipcode,
        state=state,
        vendors__in=[vendor],
    )
    if check_if_exist:
        raise exceptions.DuplicateError("address already exists")
    if state.id == get_address.state.id:
        result = await get_address.update_from_dict(
            dict(
                **payload.dict(exclude={"state", "phones"}),
                phones=",".join(payload.phones),
            )
        )
    else:
        result = await get_address.update_from_dict(
            dict(
                **payload.dict(exclude={"state", "phones"}),
                state=state,
                phones=",".join(payload.phones),
            )
        )

    if check_if_exist:
        await get_address.save()
        return result
    raise exceptions.ServerError("Could not update address")


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
        raise exceptions.NotFoundError("Shipping address not found")
    await get_address.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def vendor_delete(
    address_id: uuid.UUID,
    vendor: Vendor,
) -> Response:
    get_address = await models.Address.get_or_none(id=address_id, vendors__in=[vendor])
    if not get_address:
        raise exceptions.NotFoundError("address not found")
    await get_address.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
