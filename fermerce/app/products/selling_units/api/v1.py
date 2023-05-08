import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.users.user.models import User
from fermerce.app.products.selling_units import schemas, services
from fermerce.app.users.user.dependency import require_vendor
from fermerce.core.enum.sort_type import SortOrder

router = APIRouter(prefix="/selling_units", tags=["Product selling Unit"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_selling_unit(
    data_in: schemas.IProductSellingUnitIn, user: User = Depends(require_vendor)
):
    return await services.create(data_in=data_in, user=user)


@router.get("/")
async def get_product_detail_list(
    product_id: t.Optional[str] = Query(
        default="", description="filter through a specific product"
    ),
    select: t.Optional[str] = Query(
        default="", alias="select", description="select specific attributes"
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
    load_related: t.Optional[bool] = False,
):
    return await services.filter(
        per_page=per_page,
        page=page,
        product_id=product_id,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
    )


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
    return await services.delete(data_in=data_in, user=user)


@router.get("/", response_model=t.List[schemas.IProductSellingUnitOut])
async def get_product_selling_unit(
    product_id: uuid.UUID, user: User = Depends(require_vendor)
):
    return await services.get_product_selling_units(product_id=product_id, user=user)
