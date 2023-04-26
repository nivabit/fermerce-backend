import typing as t
import uuid
from fastapi import Request, status
from tortoise import fields
from fastapi import Response
from tortoise.expressions import Q
from fermerce.app.markets.country.models import Country
from fermerce.app.markets.state.models import State
from fermerce.app.medias.models import Media
from fermerce.app.products.product.models import Product
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount, IResponseMessage
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SearchType
from fermerce.lib.errors import error
from fermerce.app.business.vendor import schemas, models


async def create(user: User, request: Request, data_in=schemas.IVendorIn):
    check_vendor = await models.Vendor.get_or_none(user=user.id)
    if check_vendor:
        raise error.BadDataError("Business account already exist")
    check_business_name = await models.Vendor.get_or_none(business_name=data_in.business_name)
    if check_business_name:
        raise error.BadDataError("Business account already")
    to_create = dict(business_name=data_in.business_name)
    if data_in.logo:
        logo = await Media.create(
            url=Media.convert_image_name_to_url(
                media_url=f"{uuid.uuid4()}.{data_in.logo.split('.')[-1]}",
                request=request,
            ),
            uri=data_in.logo,
        )
        to_create.update({"logo": logo})
    new_vendor = await models.Vendor.create(**to_create, user=user)
    if new_vendor:
        if data_in.states:
            get_states = await State.filter(id__in=data_in.states)
            if get_states:
                await new_vendor.states.add(*get_states)
        if data_in.countries:
            get_countries = await Country.filter(id__in=data_in.countries)
            if get_countries:
                await new_vendor.countries.add(*get_countries)
        return IResponseMessage(message="Vendor account was created successfully")
    raise error.ServerError("Error creating business account")


async def update(vendor_id: uuid.UUID, user: User, request: Request, data_in=schemas.IVendorIn):
    check_vendor = await models.Vendor.get_or_none(user=user.id)
    if not check_vendor:
        raise error.NotFoundError("Business Not found")
    check_business_name = await models.Vendor.get_or_none(business_name=data_in.business_name)
    if check_vendor.id != check_business_name.id:
        if check_business_name:
            raise error.BadDataError(f"Business with name {data_in.business_name} already")
    to_update = dict(business_name=data_in.business_name)
    if data_in.logo:
        logo = await Media.create(
            url=Media.convert_image_name_to_url(media_url=data_in.logo, request=request)
        )
        to_update.update({"logo": logo})
    check_vendor.update_from_dict(to_update)
    await check_vendor.save()
    if data_in.states:
        get_states = await State.filter(id__in=data_in.states).all()
        current_state = check_vendor.states.all()
        for index, state in enumerate(get_states):
            if state in current_state:
                get_states.pop(index)
        if get_states:
            await check_vendor.states.add(*get_states)
    if data_in.countries:
        get_countries = await Country.filter(id__in=data_in.states).all()
        current_countries = check_vendor.countries.all()
        for index, country in enumerate(get_countries):
            if country in current_countries:
                get_countries.pop(index)
        if get_countries:
            await check_vendor.countries.add(*get_states)
    return IResponseMessage(message="Vendor account was updated successfully")


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    is_active: bool = False,
    is_suspended: bool = False,
    is_archived: bool = False,
    search_type: SearchType = SearchType._and,
) -> t.List[models.Vendor]:
    offset = (page - 1) * per_page
    limit = per_page

    # Query the model with the filter and pagination parameters.
    query = None
    if search_type == SearchType._or:
        query = models.Vendor.filter(
            Q(is_active=is_active) | Q(is_archived=is_archived) | Q(is_suspended=is_suspended)
        )
    else:
        query = models.Vendor.filter(
            Q(is_active=is_active),
            Q(is_suspended=is_suspended),
            Q(is_archived=is_archived),
        )

    query = query.all().offset(offset).limit(limit)
    if sort_by == SortOrder.asc and bool(order_by):
        query = query.order_by(
            *[f"-{col}" for col in order_by.split(",") if col in models.Vendor._meta.fields]
        )
    elif sort_by == SortOrder.desc and bool(order_by):
        query = query.order_by(
            *[f"{col}" for col in order_by.split(",") if col in models.Vendor._meta.fields]
        )
    else:
        query = query.order_by("-id")
    to_pre_fetch = set.union(
        models.Vendor._meta.m2m_fields,
        models.Vendor._meta.fk_fields,
        models.Vendor._meta.o2o_fields,
        models.Vendor._meta.backward_o2o_fields,
        models.Vendor._meta.backward_fk_fields,
    )

    if load_related:
        query = query.prefetch_related(*to_pre_fetch)
    if select:
        query = query.values(
            *[
                col.strip()
                for col in select.split(",")
                if col.strip() in models.Vendor._meta.fields and col.strip() not in to_pre_fetch
            ]
        )
    results = await query
    items_list = []
    items = {}
    if load_related and results and not select:
        for result in results:
            # return results
            for field_name in models.Vendor._meta.m2m_fields:
                if hasattr(result, field_name):
                    items[field_name] = list(getattr(result, field_name))
            for field_name in models.Vendor._meta.fk_fields:
                if getattr(result, field_name):
                    items[field_name] = dict(getattr(result, field_name))
            for field_name in models.Vendor._meta.o2o_fields:
                if getattr(result, field_name):
                    items[field_name] = dict(getattr(result, field_name))
            for field_name in models.Vendor._meta.backward_o2o_fields:
                if getattr(result, field_name):
                    items[field_name] = dict(getattr(result, field_name))
            for field_name in models.Vendor._meta.backward_fk_fields:
                print([dict(item) for item in list(getattr(result, field_name))])
                if getattr(result, field_name):
                    items[field_name] = list(getattr(result, field_name))
            items.update(dict(result))
            items_list.append(items)
    results = [schemas.IVendorOutFull(**item) for item in items_list]

    # Count the total number of results with the same filter.

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None

    # Return the pagination information and results as a dictionary
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(items_list),
        "results": items_list,
    }


async def remove_vendor_data(data_in: schemas.IRemoveVendor) -> None:
    vendor_to_remove = await models.Vendor.get_or_none(id=data_in.vendor_id)
    if vendor_to_remove:
        if data_in.permanent:
            await vendor_to_remove.delete()
        else:
            await vendor_to_remove.update_from_dict(dict(is_active=False, archived=True))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise error.NotFoundError(f"Vendor with vendor_id {data_in.vendor_id} does not exist")


async def get_vendor_details(vendor_id: str, load_related: bool = False):
    query = models.Vendor.get_or_none(id=vendor_id)
    if load_related:
        to_pre_fetch = set.union(
            models.Vendor._meta.m2m_fields,
            models.Vendor._meta.fk_fields,
            models.Vendor._meta.o2o_fields,
            models.Vendor._meta.backward_o2o_fields,
            models.Vendor._meta.backward_fk_fields,
        )
        query = query.prefetch_related(*to_pre_fetch)
    if not load_related:
        query = query.prefetch_related(
            *models.Vendor._meta.fk_fields, *models.Vendor._meta.o2o_fields
        )
    result = await query
    if not result:
        raise error.NotFoundError()
    if not load_related and result:
        return schemas.IVendorOut.from_orm(result)
    if result and load_related:
        items = {
            field_name: list(getattr(result, field_name))
            if hasattr(result, field_name) and field_name in models.Vendor._meta.m2m_fields
            else dict(getattr(result, field_name))
            if field_name in models.Vendor._meta.fk_fields
            or field_name in models.Vendor._meta.o2o_fields
            or field_name in models.Vendor._meta.backward_o2o_fields
            else list(getattr(result, field_name))
            if field_name in models.Vendor._meta.backward_fk_fields
            else None
            for field_name in to_pre_fetch
        }
        items = dict(**dict(result), **items)
        return schemas.IVendorOutFull(**items)


async def get_total_Vendors():
    total_count = await models.Vendor.all().count()
    return ITotalCount(count=total_count)
