import typing as t
from fastapi import APIRouter, Depends, Response, status
from fermerce.app.staff.dependency import require_super_admin_or_admin
from fermerce.app.reviews import services
from fermerce.app.user.models import User


router = APIRouter(prefix="/reviews", tags=["Product Review"])


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str, _: User = Depends(require_super_admin_or_admin)
) -> Response:
    return await services.delete(review_id=review_id)
