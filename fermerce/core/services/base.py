from fermerce.core.enum.sort_type import SortOrder
from tortoise.models import Model


def remove_password(objec):
    if isinstance(objec, list):
        for obj in objec:
            if isinstance(obj, dict):
                if obj.get("password", None):
                    del obj["password"]
            if isinstance(obj, list):
                if "password" in obj:
                    obj.pop("password", None)
    if isinstance(objec, dict):
        if objec.get("user"):
            user_data = dict(**objec.get("user", None))
            if user_data.get("password", None):
                del objec["user"]["password"]
        if objec.get("password", None):
            del objec["password"]
    if isinstance(objec, dict):
        if objec.get("auths", None):
            del objec["auths"]
    return objec


async def filter_and_list(
    model: Model,
    query: Model,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
):
    offset = (page - 1) * per_page
    limit = per_page

    # Query the model with the filter and pagination parameters.
    query = query
    query = query.all().offset(offset).limit(limit)
    if sort_by == SortOrder.asc and bool(order_by):
        query = query.order_by(
            *[
                f"-{col}"
                for col in order_by.split(",")
                if col in model._meta.fields
            ]
        )
    elif sort_by == SortOrder.desc and bool(order_by):
        query = query.order_by(
            *[
                f"{col}"
                for col in order_by.split(",")
                if col in model._meta.fields
            ]
        )
    else:
        query = query.order_by("-id")
    to_pre_fetch = set.union(
        model._meta.m2m_fields,
        model._meta.fk_fields,
        model._meta.o2o_fields,
        model._meta.backward_o2o_fields,
        model._meta.backward_fk_fields,
    )

    if load_related:
        query = query.prefetch_related(*to_pre_fetch)
    if select:
        query = query.values(
            *[
                col.strip()
                for col in select.split(",")
                if col.strip() in model._meta.fields
                and col.strip() not in to_pre_fetch
            ]
        )
    results = await query
    items_list = []
    items = {}
    if load_related and results and not select:
        for result in results:
            # return results
            for field_name in model._meta.m2m_fields:
                if hasattr(result, field_name):
                    items[field_name] = remove_password(
                        list(getattr(result, field_name))
                    )
            for field_name in model._meta.fk_fields:
                if getattr(result, field_name):
                    items[field_name] = remove_password(
                        dict(getattr(result, field_name))
                    )
            for field_name in model._meta.o2o_fields:
                if getattr(result, field_name):
                    items[field_name] = remove_password(
                        dict(getattr(result, field_name))
                    )
            for field_name in model._meta.backward_o2o_fields:
                if getattr(result, field_name):
                    items[field_name] = remove_password(
                        dict(getattr(result, field_name))
                    )
            for field_name in model._meta.backward_fk_fields:
                if getattr(result, field_name):
                    items[field_name] = remove_password(
                        list(getattr(result, field_name))
                    )
            items.update(remove_password(dict(result)))
            items_list.append(items)
    else:
        items_list = remove_password([dict(item) for item in results])

    # Count the total number of results with the same filter.

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(items_list) else None
    # Return the pagination information and results as a dictionary
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(items_list),
        "results": items_list,
    }


async def filter_and_single(
    model: Model,
    query: Model,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
):
    query = query
    if sort_by == SortOrder.asc and bool(order_by):
        query = query.order_by(
            *[
                f"-{col}"
                for col in order_by.split(",")
                if col in model._meta.fields
            ]
        )
    elif sort_by == SortOrder.desc and bool(order_by):
        query = query.order_by(
            *[
                f"{col}"
                for col in order_by.split(",")
                if col in model._meta.fields
            ]
        )
    else:
        query = query.order_by("-id")
    to_pre_fetch = set.union(
        model._meta.m2m_fields,
        model._meta.fk_fields,
        model._meta.o2o_fields,
        model._meta.backward_o2o_fields,
        model._meta.backward_fk_fields,
    )

    if load_related:
        query = query.prefetch_related(*to_pre_fetch)
    if select:
        query = query.values(
            *[
                col.strip()
                for col in select.split(",")
                if col.strip() in model._meta.fields
                and col.strip() not in to_pre_fetch
            ]
        )
    result = await query.first()
    if not result:
        return None
    item = {}
    if load_related and result and not select:
        for field_name in model._meta.m2m_fields:
            if hasattr(result, field_name):
                item[field_name] = remove_password(
                    list(getattr(result, field_name))
                )
        for field_name in model._meta.fk_fields:
            if getattr(result, field_name):
                item[field_name] = remove_password(
                    dict(getattr(result, field_name))
                )
        for field_name in model._meta.o2o_fields:
            if getattr(result, field_name):
                item[field_name] = remove_password(
                    dict(getattr(result, field_name))
                )
        for field_name in model._meta.backward_o2o_fields:
            if getattr(result, field_name):
                item[field_name] = remove_password(
                    dict(getattr(result, field_name))
                )
        for field_name in model._meta.backward_fk_fields:
            if getattr(result, field_name):
                item[field_name] = remove_password(
                    list(getattr(result, field_name))
                )
    if load_related:
        return remove_password(dict(item, **dict(result)))
    return remove_password(dict(result))
