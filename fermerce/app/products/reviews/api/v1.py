import typing as t
import uuid
from fastapi import APIRouter, Depends, status
from fermerce.app.products.reviews import schemas, services
from fermerce.app.users.user.models import User
from fermerce.app.users.user.dependency import require_user
from fermerce.core.schemas.response import ITotalCount


router = APIRouter(prefix="/reviews", tags=["Product Review"])


@router.get("/total", response_model=int)
async def get_total_reviews() -> t.Optional[int]:
    return await services.get_total_count()


@router.post(
    "/",
    response_model=schemas.IReviewOut,
    status_code=status.HTTP_200_OK,
)
async def update_review(
    data_in: schemas.IReviewIn,
    user: User = Depends(require_user),
):
    return await services.update(data_in=data_in, user=user)


@router.get(
    "/total/count",
    response_model=ITotalCount,
    status_code=status.HTTP_200_OK,
)
async def get_review_count():
    return await services.get_total_count()


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
)
async def get_products_reviews(product_id: uuid.UUID, page: int, per_page: int):
    return await services.get_product_reviews(product_id=product_id, page=page, per_page=per_page)
