import typing as t
import uuid
from esmerald import APIView, Inject, Injects, delete, get, post, put, status
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.market.category import schemas, services
from fermerce.lib.utils.base_response import IFilterList
from fermerce.lib.utils.list_endpoint_query_params import QueryType, query_params


class ProductCategoryAPIView(APIView):
    tags = ["Product Category"]
    path = "/categories"
    dependencies = {"service": Inject(services.ProductCategoryRepository)}

    @post("/", status_code=status.HTTP_201_CREATED)
    async def create_product_category(
        self,
        payload: schemas.ProductCategoryIn,
        service: services.ProductCategoryRepository = Injects(),
    ) -> schemas.ProductCategoryOut:
        return await service.create(payload=payload)

    @get("/", dependencies={"params": Inject(query_params)})
    async def get_product_category_list(
        self,
        params: QueryType = Injects(),
        service: services.ProductCategoryRepository = Injects(),
    ) -> IFilterList:
        return await service.get_list(params)

    @get("/{product_category_id}")
    async def get_product_category(
        self,
        product_category_id: uuid.UUID,
        service: services.ProductCategoryRepository = Injects(),
    ) -> schemas.ProductCategoryOut:
        return await service.get(product_category_id=product_category_id)

    @put("/{product_category_id}")
    async def update_product_category(
        self,
        product_category_id: uuid.UUID,
        permission: schemas.ProductCategoryIn,
        service: services.ProductCategoryRepository = Injects(),
    ) -> schemas.ProductCategoryOut:
        return await service.update(
            product_category_id=product_category_id, payload=permission
        )

    @get("/total/count")
    async def get_total_product_category(
        self,
        service: services.ProductCategoryRepository = Injects(),
    ) -> t.Optional[ITotalCount]:
        return await service.get_total_count()

    @delete("/{product_category_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_product_category(
        self,
        product_category_id: uuid.UUID,
        service: services.ProductCategoryRepository = Injects(),
    ) -> None:
        return await service.delete(product_category_id=product_category_id)
