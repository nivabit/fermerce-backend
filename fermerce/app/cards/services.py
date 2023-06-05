import uuid
import typing as t
from tortoise.expressions import Q
from fermerce.app.user.models import User
from fermerce.core.schemas.response import IResponseMessage
from fermerce.app.cards import models
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.lib.paystack.charge.schemas import IAuthorization


async def save_card(user: User, data_in: IAuthorization) -> models.SaveCard:
    check_card_limit = await models.SaveCard.filter(user=user).count()
    if check_card_limit > 4:
        raise error.BadDataError("Card limit exceeded")
    new_card = await models.SaveCard.create(**data_in.dict(), user=user)
    if new_card:
        return new_card
    raise error.ServerError("Could not save card")


async def remove_saved_card(
    card_id: uuid.UUID,
    user: User,
) -> IResponseMessage:
    get_card = await models.SaveCard.get_or_none(id=card_id, user=user)
    if get_card:
        await get_card.delete()
        return IResponseMessage(message="card was removed successfully")
    raise error.NotFoundError("Card is not found")


async def get_saved_card(
    card_id: uuid.UUID,
    user: User,
    load_related: bool = False,
) -> models.SaveCard:
    query = models.SaveCard.filter(id=card_id, user=user)
    get_card = await filter_and_single(
        query=query,
        model=models.SaveCard,
        load_related=load_related,
    )
    if get_card:
        return get_card
    raise error.NotFoundError("Card is not found")


async def get_saved_cards(
    user: User,
    filter_string: str,
    load_related: bool = False,
) -> t.List[models.SaveCard]:
    query = models.SaveCard.filter(user=user)
    if filter_string:
        query = query.filter(
            Q(card_type__icontains=filter_string)
            | Q(brand__icontains=filter_string)
            | Q(bank__icontains=filter_string)
        )
    get_cards = await filter_and_list(
        query=query,
        model=models.SaveCard,
        load_related=load_related,
    )
    return get_cards
