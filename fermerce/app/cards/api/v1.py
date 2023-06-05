import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.cards import services
from fermerce.app.user.models import User
from fermerce.app.user import dependency
from fermerce.lib.paystack.charge.schemas import IAuthorization

router = APIRouter(prefix="/cards", tags=["Saved payment Card"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_card(
    data_in: IAuthorization,
    user: User = Depends(dependency.require_user),
):
    return await services.create(data_in=data_in, user=user)


@router.get("/")
async def get_cards(
    filter_string: str = Query(
        default=None, description="filter through product on the category"
    ),
    select: t.Optional[str] = Query(
        default="", description="order by attribute, e.g. id, created_at"
    ),
    load_related: bool = False,
    user: User = Depends(dependency.require_user),
):
    return await services.get_saved_cards(
        user=user,
        filter_string=filter_string,
        load_related=load_related,
        select=select,
    )


@router.get("/{card_id}", status_code=status.HTTP_200_OK)
async def get_card(
    card_id: uuid.UUID,
    user: User = Depends(dependency.require_user),
    load_related: bool = False,
):
    return await services.get_saved_card(
        card_id=card_id,
        user=user,
        load_related=load_related,
    )


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: uuid.UUID, user: User = Depends(dependency.require_user)
):
    return await services.delete(card_id, user)
