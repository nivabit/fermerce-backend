import uuid
import typing as t
from fastapi import status
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
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


# # get all permissions
async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
) -> t.List[models.ProductCategory]:
    offset = (page - 1) * per_page
    limit = per_page

    # Construct a Q object to filter the results by the filter string.
    # filter_q = Q()

    # for field in models.ProductCategory._meta.fields_map.values():
    #     if field.internal:
    #         continue
    #     if field.unique:
    #         filter_q |= Q(**{f"{field.name}": filter_string})
    #     elif field.__class__.__name__ == "TextField":
    #         filter_q |= Q(**{f"{field.name}__icontains": filter_string})
    #     elif field.__class__.__name__ in ["CharField", "ForeignKeyField"]:
    #         filter_q |= Q(**{f"{field.name}__icontains": filter_string})

    # Query the model with the filter and pagination parameters.
    results = await models.ProductCategory.all().offset(offset).limit(limit)

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


async def get_total_count() -> ITotalCount:
    total = await models.ProductCategory.all().count()
    return ITotalCount(count=total).dict()


# # update permission
async def update(
    product_category_id: uuid.UUID,
    data_in: schemas.IProductCategoryIn,
) -> models.ProductCategory:
    check_product_category = await models.ProductCategory.get_or_none(id=product_category_id)
    if not check_product_category:
        raise error.NotFoundError("product category does not exist")
    check_name = await models.ProductCategory.get_or_none(name=data_in.name)
    if check_name and check_name.id != product_category_id:
        raise error.DuplicateError("product category already exists")
    await models.ProductCategory.filter(id=product_category_id).update(**data_in.dict())
    return check_product_category


# # delete permission
async def delete(
    product_category_id: uuid.UUID,
) -> None:
    deleted_product_category = await models.ProductCategory.filter(id=product_category_id).delete()
    if not deleted_product_category:
        raise error.NotFoundError("product category does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
