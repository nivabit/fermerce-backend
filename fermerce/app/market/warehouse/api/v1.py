import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from fermerce.app.staff.dependency import require_super_admin_or_admin
from fermerce.app.warehouse import schemas, services
from fermerce.core.enum.sort_type import SortOrder

router = APIRouter(prefix="/warehouses", tags=["Warehouse"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_warehouse(data_in: schemas.IWarehouseIn):
    return await services.vendor_create(
        data_in=data_in,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_warehouse_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all through attributes"
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc,
        description="order by attribute, e.g. id",
    ),
    order_by: t.Optional[str] = Query(
        default="id",
        description="order by attribute, e.g. id",
    ),
    load_related: bool = False,
):
    return await services.warehouse_filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )


@router.get("/{warehouse_id}", status_code=status.HTTP_200_OK)
async def get_warehouse(
    warehouse_id: uuid.UUID,
    load_related: bool = False,
):
    return await services.vendor_get(
        warehouse_id=warehouse_id,
        load_related=load_related,
    )


@router.put("/{warehouse_id}", status_code=status.HTTP_200_OK)
async def update_warehouse(
    warehouse_id: uuid.UUID,
    data_in: schemas.IWarehouseIn,
):
    return await services.update(
        warehouse_id=warehouse_id,
        data_in=data_in,
    )


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(warehouse_id: uuid.UUID) -> Response:
    return await services.vendor_delete(
        warehouse_id=warehouse_id,
    )
