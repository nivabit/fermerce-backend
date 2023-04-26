import uuid
import typing as t
from fastapi import status
from fermerce.app.products.measuring_unit.models import MeasuringUnit
from fermerce.app.users.user.models import User
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.errors import error
from fermerce.app.products.selling_units import schemas, models
from fermerce.app.products.product.models import Product
from fastapi import Response


async def create(data_in: schemas.IProductSellingUnitIn, user: User) -> models.ProductSellingUnit:
    get_product = await Product.get_or_none(pk=data_in.product_id, vender=user.vendor)
    if not get_product:
        raise error.NotFoundError("Product not found")
    get_measuring_unit = await MeasuringUnit.get_or_none(id=data_in.unit_id)
    if not get_measuring_unit:
        raise error.NotFoundError("measuring unit not found")
    check_existing_unit = await models.ProductSellingUnit.get_or_none(
        unit=get_measuring_unit, product=get_product
    )
    if check_existing_unit:
        raise error.DuplicateError(
            f"Measuring unit {get_measuring_unit.unit} already exists for this product"
        )
    selling_unit = await models.ProductSellingUnit.create(
        product=get_product,
        unit=get_measuring_unit,
        price=data_in.price,
        size=data_in.size,
    )
    if not selling_unit:
        raise error.ServerError("Error creating new product measure unit")
    return IResponseMessage(message="Product measure unit created successfully")


async def get_selling_unit(
    selling_unit_id: uuid.UUID, user: User
) -> t.List[models.ProductSellingUnit]:
    get_selling_unit = await models.ProductSellingUnit.get_or_none(
        pk=selling_unit_id, product__vendor=user.vendor
    )
    return get_selling_unit


async def get_product_selling_units(
    product_id: uuid.UUID, user: User
) -> t.List[models.ProductSellingUnit]:
    get_selling_unit = await models.ProductSellingUnit.filter(
        product=product_id, product__vendor=user.vendor
    ).all()
    return get_selling_unit


async def update(data_in: schemas.IProductSellingUnitIn, user: User) -> models.ProductSellingUnit:
    selling_unit = await models.ProductSellingUnit.get_or_none(
        product=data_in.product_id, unit=data_in.unit_id, product__vendor=user.vendor
    )
    if not selling_unit:
        raise error.NotFoundError("selling unit not found")
    selling_unit.update_from_dict(data_in.dict(exclude={"product_id", "unit_id"}))
    try:
        await selling_unit.save()
        return selling_unit
    except:
        raise error.ServerError("error updating product selling unit")


async def delete(
    data_in: schemas.IProductRemoveSellingUnitIn, user: User
) -> models.ProductSellingUnit:
    selling_unit = await models.ProductSellingUnit.get_or_none(
        product=data_in.product_id, unit=data_in.unit_id, product__vendor=user.vendor
    )
    if not selling_unit:
        raise error.NotFoundError("selling unit does not exists for this product")
    try:
        await selling_unit.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except:
        raise error.ServerError("error deleting product selling unit")
