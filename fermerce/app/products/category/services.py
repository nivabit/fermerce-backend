import uuid
import typing as t
from fastapi import status
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
from fermerce.core.services.base import filter_and_list
from fermerce.lib.errors import error
from fermerce.app.products.category import schemas, models
from fastapi import Response


# create permission
async def create(
    data_in: schemas.IProductCategoryIn,
) -> models.ProductCategory:
    check_product_category = await models.ProductCategory.get_or_none(name=data_in.name)
    if check_product_category:
        raise error.DuplicateError("product category already exists")
    new_type = await models.ProductCategory.create(**data_in.dict())
    if not new_type:
        raise error.ServerError("Internal server error")
    return new_type


async def get(
    product_category_id: uuid.UUID,
) -> models.ProductCategory:
    product_category = await models.ProductCategory.get_or_none(id=product_category_id)
    if not product_category:
        raise error.NotFoundError("product category not found")
    return product_category


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = None,
    order_by: str = None,
    sort_by: SortOrder = SortOrder.asc,
) -> t.List[models.ProductCategory]:
    query = models.ProductCategory
    if filter_string:
        query = query.filter(name__icontains=filter_string)

    results = await filter_and_list(
        model=models.ProductCategory,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )

    return results


async def get_total_count() -> ITotalCount:
    total = await models.ProductCategory.all().count()
    return ITotalCount(count=total).dict()


# # update permission
async def update(
    product_category_id: uuid.UUID,
    data_in: schemas.IProductCategoryIn,
) -> models.ProductCategory:
    check_product_category = await models.ProductCategory.get_or_none(
        id=product_category_id
    )
    if not check_product_category:
        raise error.NotFoundError("product category does not exist")
    check_name = await models.ProductCategory.get_or_none(name=data_in.name)
    if check_name and check_name.id != product_category_id:
        raise error.DuplicateError("product category already exists")
    check_product_category.update_from_dict(data_in.dict())
    await check_product_category.save()
    return check_product_category


# # delete permission
async def delete(
    product_category_id: uuid.UUID,
) -> None:
    deleted_product_category = await models.ProductCategory.filter(
        id=product_category_id
    ).delete()
    if not deleted_product_category:
        raise error.NotFoundError("product category does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
