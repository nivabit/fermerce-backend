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
from fermerce.core.services.base import filter_and_list, filter_and_single
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


async def get(slug: str, load_related: bool) -> schemas.IProductOut:
    query = models.Product.filter(slug=slug)
    result = await filter_and_single(query=query, load_related=load_related, model=models.Product)
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
    is_suspended: bool = False,
    in_stock: bool = False,
    search_type: SearchType = SearchType._or,
) -> t.List[schemas.IProductListOut]:
    query = None
    if search_type == SearchType._or:
        query = models.Product.filter(Q(in_stock=in_stock) | Q(is_suspended=is_suspended))
    else:
        query = models.Product.filter(
            Q(in_stock=in_stock),
            Q(is_suspended=is_suspended),
            Q(is_suspended=is_suspended),
            Q(name__icontains=filter_string),
            Q(slug__icontains=filter_string),
            Q(details__description__icontains=filter_string),
            Q(details__title__icontains=filter_string),
            Q(sku__icontains=filter_string),
            Q(categories__name__icontains=filter_string),
        )
    if filter_string:
        query = query.filter(
            Q(in_stock=in_stock)
            | Q(is_suspended=is_suspended)
            | Q(is_suspended=is_suspended)
            | Q(name__icontains=filter_string)
            | Q(slug__icontains=filter_string)
            | Q(description__icontains=filter_string)
            | Q(details__title__icontains=filter_string)
            | Q(details__description__icontains=filter_string)
            | Q(sku__icontains=filter_string)
            | Q(categories__name__icontains=filter_string)
        )
        query = query.filter(
            Q(vendor__business_name__icontains=filter_string),
            Q(vendor__is_suspended=False),
        )
    result = await filter_and_list(
        model=models.Product,
        query=query,
        page=page,
        load_related=load_related,
        per_page=per_page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )
    return result


async def get_product_count() -> ITotalCount:
    total = await models.Product.all().count()
    return ITotalCount(count=total)


async def delete(product_id: uuid.UUID, user: User):
    get_product = await models.Product.get_or_none(vendor=user.vendor, id=product_id)
    if not get_product:
        raise error.NotFoundError("Product not found")
    await get_product.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
