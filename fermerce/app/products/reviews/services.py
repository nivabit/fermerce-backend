import typing as t
import uuid
from fastapi import status, Response
from fermerce.app.users.user.models import User
from fermerce.lib.errors import error
from fermerce.app.products.reviews import schemas, models


async def update(
    data_in: schemas.IReviewIn,
    user: User,
) -> models.Review:
    check_review = await models.Review.get_or_none(id=data_in.review_id, user=user)
    if not check_review:
        raise error.NotFoundError("Product does not exist")
    if check_review.edit_limit == 3:
        raise error.ForbiddenError("You have reached the edit limit")
    check_review.update_from_dict(
        data_in.dict(
            exclude={"product_id", "review_id"},
            reviewed=True,
            user=user,
            edit_limit=check_review.edit_limit + 1,
        )
    )
    try:
        await check_review.save()
        return check_review
    except:
        raise error.ServerError("error updating review")


async def get_product_reviews(
    product_id: uuid.UUID, page: int, per_page: int
) -> t.List[models.Review]:
    offset = (page - 1) * per_page
    limit = per_page
    get_reviews = (
        await models.Review.filter(id=product_id)
        .all()
        .limit(limit)
        .offset(offset)
        .order_by("-created")
    )
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(get_reviews) else None

    # Return the pagination information and results as a dictionary
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(get_reviews),
        "results": get_reviews,
    }


async def get_total_count() -> int:
    return await models.Review.all().count()


async def delete(
    review_id: str,
) -> None:
    get_review = await models.Review.get_or_none(id=review_id)
    if not get_review:
        raise error.NotFoundError("Review does not exist")
    await get_review.delete(get_review.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
