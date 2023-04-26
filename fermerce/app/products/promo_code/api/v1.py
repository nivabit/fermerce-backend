import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.users.user.models import User
from fermerce.core.schemas.response import IResponseMessage, ITotalCount
from fermerce.app.products.promo_code import schemas, services
from fermerce.app.users.user.dependency import require_vendor


router = APIRouter(prefix="/promocodes", tags=["Product Promo Codes"])


@router.post(
    "/",
    response_model=schemas.IProductPromoCodeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_promo_code(
    data_in: schemas.IProductPromoCodeIn, user: User = Depends(require_vendor)
) -> schemas.IProductPromoCodeOut:
    return await services.create(data_in=data_in, user=user)


@router.get("/", response_model=t.List[schemas.IProductPromoCodeOut])
async def get_promo_code_list(
    user: User = Depends(require_vendor),
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all promo codes"
    ),
    per_page: int = 10,
    page: int = 1,
):
    return await services.filter(
        filter_string=filter_string, per_page=per_page, page=page, user=user
    )


@router.get("/{promo_code_id}", response_model=schemas.IProductPromoCodeOut)
async def get_promo_code(
    promo_code_id: uuid.UUID, user: User = Depends(require_vendor)
) -> schemas.IProductPromoCodeOut:
    return await services.get(promo_code_id=promo_code_id, user=user)


@router.put("/{promo_code_id}", response_model=schemas.IProductPromoCodeOut)
async def update_promo_code(
    promo_code_id: uuid.UUID,
    data_in: schemas.IProductPromoCodeIn,
    user: User = Depends(require_vendor),
) -> schemas.IProductPromoCodeOut:
    return await services.update(promo_code_id=promo_code_id, data_in=data_in, user=user)


@router.get("/total/count", response_model=ITotalCount)
async def get_total_promo_code(
    user: User = Depends(require_vendor),
) -> t.Optional[ITotalCount]:
    return await services.get_total_count(user)


@router.post("/products", status_code=status.HTTP_200_OK)
async def add_product_to_promo_code(
    data_in: schemas.IProductPromoCodeUpdateIn, user: User = Depends(require_vendor)
) -> IResponseMessage:
    return await services.add_product_to_promo_code(data_in=data_in, user=user)


@router.delete("/products", status_code=status.HTTP_200_OK)
async def remove_product_from_promo_code(
    data_in: schemas.IProductPromoCodeRemoveIn, user: User = Depends(require_vendor)
) -> IResponseMessage:
    return await services.delete_product_from_promo_code(data_in=data_in, user=user)


@router.delete("/{promo_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promo_code(promo_code_id: uuid.UUID, user: User = Depends(require_vendor)) -> None:
    return await services.delete(promo_code_id=promo_code_id, user=user)
