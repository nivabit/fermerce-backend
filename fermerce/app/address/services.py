import uuid
import typing as t
from fastapi import status, Response
import tortoise
from tortoise.expressions import Q
from fermerce.app.address.enum import SaveTypeEnum
from fermerce.app.state.models import State
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.address import schemas, models


async def create(
    data_in: schemas.IAddressIn,
    user: User,
    save_type: SaveTypeEnum,
) -> models.Address:
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("shipping state not found")
    if save_type.customer:
        check_address = await models.Address.get_or_none(
            street=data_in.street,
            city=data_in.city,
            zipcode=data_in.zipcode,
            state=get_state,
        ).select_related("user")
        if check_address and check_address.user:
            raise error.DuplicateError("business address already exists")
        new_address = await models.Address.create(
            **data_in.dict(exclude={"state", "phones"}),
            state=get_state,
            phones=",".join(data_in.phones),
            user=user
        )
    elif save_type == save_type.vendor:
        try:
            check_address = await models.Address.get_or_none(
                street=data_in.street,
                city=data_in.city,
                zipcode=data_in.zipcode,
                state=get_state,
            ).select_related("vendor")
            if check_address and check_address.vendor:
                raise error.DuplicateError("business address already exists")
            new_address = await models.Address.create(
                **data_in.dict(exclude={"state", "phones"}),
                state=get_state,
                phones=",".join(data_in.phones),
                vendor=user.vendor
            )
        except tortoise.exceptions.NoValuesFetched:
            raise error.UnauthorizedError()
        if new_address:
            return new_address

    new_address = await models.Address.create(
        **data_in.dict(exclude={"state", "phones"}),
        state=get_state,
        phones=",".join(data_in.phones)
    )

    if new_address:
        await user.shipping_address.add(new_address)
        return new_address
    raise error.ServerError("error creating new shipping address")


async def get(
    address_id: uuid.UUID,
    user: User,
    get_type: SaveTypeEnum,
    load_related: bool = False,
) -> models.Address:
    query = models.Address.filter(id=address_id)
    if get_type == get_type.customer:
        check_owner = await models.Address.get_or_none(
            id=address_id
        ).select_related("user")
        if check_owner.user == user:
            result = await filter_and_single(
                model=models.Address,
                query=query,
                load_related=load_related,
            )
    elif get_type == get_type.vendor:
        if get_type == get_type.vendor:
            check_owner = await models.Address.get_or_none(
                id=address_id
            ).select_related("vendor")
        try:
            if check_owner.user == user.vendor:
                result = await filter_and_single(
                    model=models.Address,
                    query=query,
                    load_related=load_related,
                )
        except tortoise.exceptions.NoValuesFetched:
            raise error.NotFoundError("Shipping address not found")
    if not result:
        raise error.NotFoundError("Shipping address not found")
    return result


async def update(
    address_id: uuid.UUID,
    data_in: schemas.IAddressIn,
    save_type: SaveTypeEnum,
    user: User,
) -> models.Address:
    get_address = await models.Address.get_or_none(
        id=address_id, user=user
    ).prefetch_related("state")
    if not get_address:
        raise error.NotFoundError("Address not found")
    get_state = await State.get_or_none(id=data_in.state)
    if not get_state:
        raise error.NotFoundError("shipping state not found")
    if save_type == save_type.customer:
        check_if_exist = await models.Address.get_or_none(
            street=data_in.street,
            city=data_in.city,
            zipcode=data_in.zipcode,
            state=get_state,
        ).select_related("user")
        if (
            check_if_exist
            and check_if_exist.user == user
            and check_if_exist.id != address_id
        ):
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
    if save_type == save_type.vendor:
        try:
            check_if_exist = await models.Address.get_or_none(
                street=data_in.street,
                city=data_in.city,
                zipcode=data_in.zipcode,
                state=get_state,
            ).select_related("vendor")
            if (
                check_if_exist
                and check_if_exist.user == user
                and check_if_exist.id != address_id
            ):
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
        except tortoise.exceptions.NoValuesFetched:
            raise error.UnauthorizedError()
    try:
        await get_address.save()
        return result
    except:
        raise error.ServerError("Could not update address")


async def filter(
    user: User,
    get_type: SaveTypeEnum,
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
    if get_type == SaveTypeEnum.customer and user:
        query = query.filter(user=user)
    elif get_type == SaveTypeEnum.vendor and user:
        try:
            query.filter(user=user.vendor)
        except tortoise.exceptions.NoValuesFetched:
            return []
    return await filter_and_list(
        query=query,
        model=models.Address,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


async def get_total_count(user: User) -> dict:
    total_add = await models.Address.filter(user=user).count()
    return dict(total=len(total_add))


async def delete(
    address_id: uuid.UUID,
    user: User,
    delete_type: SaveTypeEnum,
) -> Response:
    get_address = None
    if delete_type == SaveTypeEnum.customer and user:
        get_address = await models.Address.get_or_none(id=address_id, user=user)
    elif SaveTypeEnum.vendor == delete_type:
        try:
            get_address = await models.Address.get_or_none(
                id=address_id, user=user.vendor
            )
        except tortoise.exceptions.NoValuesFetched:
            get_address = None
    else:
        get_address = await models.Address.get_or_none(id=address_id)
    if not get_address:
        raise error.NotFoundError("Shipping address not found")
    await get_address.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
