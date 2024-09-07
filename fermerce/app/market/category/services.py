import typing as t
from edgy import Q
from fastapi import status
from fermerce.app.market.category.models import ProductCategory
from fermerce.app.market.category.schemas import ProductCategoryIn
from fermerce.lib.utils.list_endpoint_query_params import QueryType
from fermerce.core.services.base import BaseRepository
from fermerce.lib.utils.base_response import (
    ICount,
    IFilterList,
    get_error_response,
)


class ProductCategoryRepository(object):
    base_doa = BaseRepository[ProductCategory](
        model=ProductCategory,
        model_name="Product Category",
    )

    @classmethod
    async def get(cls, product_category_id: str) -> ProductCategory:
        return await cls.base_doa.get(id=product_category_id, raise_error=True)

    @classmethod
    async def get_all(
        cls,
        offset: str = 0,
        limit: str = 10,
    ) -> t.List[ProductCategory]:
        return await cls.base_doa.get_all(limit=limit, offset=offset)

    @classmethod
    async def get_count(cls) -> ICount:
        return await cls.base_doa.get_count()

    @classmethod
    async def get_list(cls, params: QueryType) -> IFilterList:
        checks_list = []
        if params.filter_string:
            checks_list.append(Q(name__icontains=params.filter_string))
        return await cls.base_doa.filter_and_list(
            check_list=checks_list,
            **params.model_dump(exclude={"filter_string"}),
        )

    @classmethod
    async def create(cls, payload: ProductCategoryIn) -> ProductCategory:
        check_existing_product_category = await cls.base_doa.filter_obj(
            get_first=True,
            check=dict(name=payload.name),
            raise_error=False,
        )
        if check_existing_product_category:
            raise get_error_response(
                f"{cls.base_doa.model_name} already exists",
                status_code=status.HTTP_409_CONFLICT,
            )
        return await cls.base_doa.create(
            payload=payload,
        )

    @classmethod
    async def get_single(cls, product_category_id: str) -> ProductCategory:
        return await cls.base_doa.get_single(object_id=product_category_id)

    @classmethod
    async def update(
        cls,
        product_category_id: str,
        payload: ProductCategoryIn,
    ) -> ProductCategory:
        get_product_category = await cls.get(product_category_id=product_category_id)
        check_existing_product_category = await cls.base_doa.filter_obj(
            check=dict(name__icontains=payload.name),
            get_first=True,
            raise_error=False,
        )
        if (
            check_existing_product_category
            and check_existing_product_category.id != get_product_category.id
        ):
            raise get_error_response(
                detail=f"{cls.asset_doa.base_doa.model_name} has already exist",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return await cls.base_doa.update(
            id=product_category_id,
            payload=payload.model_dump(),
        )

    @classmethod
    async def delete(cls, category_id: str) -> ProductCategory:
        return await cls.base_doa.delete_by_id(
            object_id=category_id,
            raise_error=True,
        )
