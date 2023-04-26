import uuid
import typing as t
from fastapi import (
    Request,
    status,
    Response,
)
from tortoise.expressions import Q
from fermerce.core.enum.sort_type import SearchType, SortOrder
from fermerce.core.schemas.response import ITotalCount, IResponseMessage
from fermerce.lib.errors import error
from fermerce.app.products.product import models, schemas
from fermerce.app.products.category.models import ProductCategory
from fermerce.app.medias.models import Media
from fermerce.app.users.user.models import User


async def create(user: User, data_in: schemas.IProductIn, request: Request) -> models.Product:
    check_product = await models.Product.get_or_none(name=data_in.name, vendor=user.vendor)
    if check_product:
        raise error.DuplicateError(f"Product with name `{data_in.name}`already  exists")

    to_create = dict(
        name=data_in.name,
        description=data_in.description,
        slug=models.Product.make_slug(data_in.name),
        in_stock=data_in.in_stock,
    )
    if data_in.cover_img:
        cover_img = await Media.create(
            url=Media.convert_image_name_to_url(
                media_url=data_in.cover_img,
                request=request,
            ),
            uri=data_in.cover_img,
        )
        to_create.update({"cover_media": cover_img})
    new_product = await models.Product.create(**to_create, vendor=user.vendor)
    if data_in.categories:
        product_categories = await ProductCategory.filter(id__in=data_in.categories).all()
        if product_categories:
            await new_product.categories.add(*product_categories)

    if data_in.galleries:
        media_galleries_obj = [
            await Media.create(
                url=Media.convert_image_name_to_url(
                    media_url=media_uri,
                    request=request,
                ),
                uri=media_uri,
            )
            for media_uri in data_in.galleries
            if media_uri
        ]
        await new_product.galleries.add(*media_galleries_obj)
        if new_product:
            return IResponseMessage(message="product created successfully")
    raise error.ServerError("Error while creating product")


async def update(
    user: User, product_id: uuid.UUID, data_in: schemas.IProductIn, request: Request
) -> models.Product:
    check_product = await models.Product.get_or_none(name=data_in.name, vendor=user.vendor)
    if check_product and check_product.id != product_id:
        raise error.DuplicateError(f"Product with name `{data_in.name}`already  exists")
    if data_in.categories:
        current_categories = await check_product.categories.all()
        get_categories = await ProductCategory.filter(id__in=data_in.categories).all()
        new_categories = []
        for category in get_categories:
            if category not in current_categories:
                new_categories.append(category)
        if new_categories:
            await check_product.categories.add(*new_categories)
    to_update = dict(
        name=data_in.name,
        description=data_in.description,
        slug=models.Product.make_slug(data_in.name),
        in_stock=data_in.in_stock,
    )
    if data_in.cover_img:
        check_product_cover_media = await Media.get_or_none(cover_media=check_product.id)
        if check_product_cover_media:
            await check_product_cover_media.delete()
            await Media.create(
                url=Media.convert_image_name_to_url(media_url=data_in.cover_img, request=request),
                uri=data_in.cover_img,
            )
    if data_in.galleries:
        media_galleries_obj = [
            await Media.create(
                url=Media.convert_image_name_to_url(media_url=media_uri, request=request),
                uri=media_uri,
            )
            for media_uri in data_in.galleries
            if media_uri
        ]
        if media_galleries_obj:
            await check_product.galleries.add(*media_galleries_obj)

    updated_product = await models.Product.filter(id=product_id).update(**to_update)

    if updated_product:
        return IResponseMessage(message="product updated successfully")
    raise error.ServerError("Error while creating product")


async def get(slug: str, load_related: bool) -> models.Product:
    query = models.Product.get_or_none(slug__icontains=slug)
    if load_related:
        to_pre_fetch = set.union(
            models.Product._meta.m2m_fields,
            models.Product._meta.fk_fields,
            models.Product._meta.o2o_fields,
            models.Product._meta.backward_o2o_fields,
            models.Product._meta.backward_fk_fields,
        )
        query = query.prefetch_related(*to_pre_fetch)
    if not load_related:
        query = query.prefetch_related(
            *models.Product._meta.fk_fields, *models.Product._meta.o2o_fields
        )
    result = await query
    if not result:
        raise error.NotFoundError()
    if not load_related and result:
        return dict(result)
    if result and load_related:
        items = {
            field_name: list(getattr(result, field_name))
            if hasattr(result, field_name) and field_name in models.Product._meta.m2m_fields
            else dict(getattr(result, field_name))
            if field_name in models.Product._meta.fk_fields
            or field_name in models.Product._meta.o2o_fields
            or field_name in models.Product._meta.backward_o2o_fields
            else list(getattr(result, field_name))
            if field_name in models.Product._meta.backward_fk_fields
            else None
            for field_name in to_pre_fetch
        }
        result = dict(**dict(result), **items)

    if not result:
        raise error.NotFoundError("Product not found")
    return result


# # get all permissions
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
    in_stock: bool = False,
    search_type: SearchType = SearchType._or,
) -> t.List[models.Product]:
    offset = (page - 1) * per_page
    limit = per_page

    # Query the model with the filter and pagination parameters.
    query = None
    if search_type == SearchType._or:
        query = models.Product.filter(
            Q(is_active=is_active) | Q(in_stock=in_stock) | Q(is_suspended=is_suspended)
        )
    else:
        query = models.Product.filter(
            Q(is_active=is_active),
            Q(is_suspended=is_suspended),
            Q(in_stock=in_stock),
        )

    query = query.all().offset(offset).limit(limit)
    if sort_by == SortOrder.asc and bool(order_by):
        query = query.order_by(
            *[f"-{col}" for col in order_by.split(",") if col in models.Product._meta.fields]
        )
    elif sort_by == SortOrder.desc and bool(order_by):
        query = query.order_by(
            *[f"{col}" for col in order_by.split(",") if col in models.Product._meta.fields]
        )
    else:
        query = query.order_by("-id")
    to_pre_fetch = set.union(
        models.Product._meta.m2m_fields,
        models.Product._meta.fk_fields,
        models.Product._meta.o2o_fields,
        models.Product._meta.backward_o2o_fields,
        models.Product._meta.backward_fk_fields,
    )

    if load_related:
        query = query.prefetch_related(*to_pre_fetch)
    if select:
        query = query.values(
            *[
                col.strip()
                for col in select.split(",")
                if col.strip() in models.Product._meta.fields and col.strip() not in to_pre_fetch
            ]
        )
    results = await query
    if load_related and not select:
        results = [
            schemas.IProductLongInfo(
                **{
                    field_name: list(getattr(result, field_name))
                    if hasattr(result, field_name) and field_name in models.Product._meta.m2m_fields
                    else dict(getattr(result, field_name))
                    if field_name in models.Product._meta.fk_fields
                    or field_name in models.Product._meta.o2o_fields
                    or field_name in models.Product._meta.backward_o2o_fields
                    else list(getattr(result, field_name))
                    if field_name in models.Product._meta.backward_fk_fields
                    else None
                    for field_name in to_pre_fetch
                },
                **dict(result),
            )
            for result in results
        ]

    # Count the total number of results with the same filter.

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None

    # Return the pagination information and results as a dictionary
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


async def get_product_count() -> ITotalCount:
    total = await models.Product.all().count()
    return ITotalCount(count=total)


async def delete(product_id: uuid.UUID, user: User):
    get_product = await models.Product.get_or_none(vendor=user.vendor, id=product_id)
    if not get_product:
        raise error.NotFoundError("Product not found")
    await get_product.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


"""****************************************************Product details********************************************************************"""


async def create_details(data_in: schemas.IProductDetailsIn, user: User) -> models.ProductDetail:
    get_product = await models.Product.get_or_none(id=data_in.product_id, vendor=user.vendor)
    if not get_product:
        raise error.NotFoundError("product detail not found")
    to_create = [models.ProductDetail(**data, product=get_product) for data in data_in.details]
    created_details = await models.ProductDetail.bulk_create(to_create)
    if created_details:
        return IResponseMessage(message="Product details was created successfully")
    raise error.ServerError("error creating product details")


async def get_detail(detail_id: uuid.UUID) -> models.ProductDetail:
    product_detail = await models.ProductDetail.get_or_none(id=detail_id)
    if not product_detail:
        raise error.NotFoundError("product detail not found")
    return product_detail


async def get_product_detail(product_id: uuid.UUID) -> t.List[models.ProductDetail]:
    product_details = await models.ProductDetail.filter(product=product_id).all()
    return product_details


async def update_product_detail(
    data_in: schemas.IProductDetailsIn, user: User
) -> models.ProductDetail:
    get_product = await models.Product.get_or_none(id=data_in.product_id, vendor=user.vendor)
    if not get_product:
        raise error.NotFoundError("product not found")

    get_product_detail = await models.ProductDetail.get_or_none(
        id=data_in.detail_id, product=get_product
    )
    if not get_product_detail:
        raise error.NotFoundError("product detail does not exist")
    get_product_detail.update_from_dict(data_in.dict(exclude={"product_id", "detail_id"}))
    await get_product_detail.save()
    return get_product_detail


async def delete_product_detail(data_in: schemas.IProductDetailsRemoveIn, user: User):
    get_product = await models.Product.get_or_none(id=data_in.product_id, vendor=user.vendor)
    if not get_product:
        raise error.NotFoundError("product not found")

    get_product_detail = await models.ProductDetail.get_or_none(
        id=data_in.detail_id, product=get_product
    )
    if not get_product_detail:
        raise error.NotFoundError("Product detail not found")
    await get_product_detail.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
