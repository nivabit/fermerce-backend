import typing as t
import uuid
from fastapi import APIRouter, Depends, status
from fermerce.app.users.user.models import User
from fermerce.app.products.selling_units import schemas, services
from fermerce.app.users.user.dependency import require_vendor

router = APIRouter(prefix="/selling_units", tags=["Product selling Unit"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_selling_unit(
    data_in: schemas.IProductSellingUnitIn, user: User = Depends(require_vendor)
):
    return await services.create(data_in=data_in, user=user)


@router.get("/{selling_unit_id}", response_model=schemas.IProductSellingUnitOut)
async def get_selling_unit(
    selling_unit_id: uuid.UUID, user: User = Depends(require_vendor)
) -> schemas.IProductSellingUnitOut:
    return await services.get_selling_unit(selling_unit_id=selling_unit_id, user=user)


@router.put("/", response_model=schemas.IProductSellingUnitOut)
async def update_selling_unit(
    data_in: schemas.IProductSellingUnitIn, user: User = Depends(require_vendor)
) -> schemas.IProductSellingUnitOut:
    return await services.update(data_in=data_in, user=user)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selling_unit(
    data_in: schemas.IProductRemoveSellingUnitIn, user: User = Depends(require_vendor)
) -> None:
    return await services.delete(unit_id=data_in, user=user)


@router.get("/", response_model=t.List[schemas.IProductSellingUnitOut])
async def get_product_selling_unit(
    product_id: uuid.UUID, user: User = Depends(require_vendor)
):
    return await services.get_product_selling_units(product_id=product_id, user=user)
