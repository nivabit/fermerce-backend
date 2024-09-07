import re
from esmerald import AsyncDAOProtocol
from typing import Any, Dict, Generator, TypeVar, Generic, TYPE_CHECKING, Union
from fermerce.core.enum.sort_type import SortOrder
from edgy import Model, QuerySet

if TYPE_CHECKING:
    from esmerald.types import DictAny

modelType = TypeVar("model", bound=Model)


class BaseDAO[modelType](Generic[modelType]):
    def __init__(self, model: modelType):
        super().model = model

    async def get(self, obj_id: int, **kwargs: "DictAny") -> modelType:
        # logic to get the user
        ...

    async def get_all(self, **kwargs: "DictAny") -> list[modelType]:
        # logic to get all the users
        ...

    async def update(
        self, obj_id: int, payload: modelType, **kwargs: "DictAny"
    ) -> modelType:
        # logic to update the user
        ...

    async def delete(self, obj_id: int, **kwargs: "DictAny") -> modelType:
        # logic to delete a user
        ...

    async def create(self, payload: modelType, **kwargs: "DictAny") -> modelType:
        pass

    async def get_single(
        self,
        object_id: str,
        check: dict = None,
        check_list: list = None,
        load_related: bool = False,
        raise_error: bool = True,
        object_only: bool = False,
    ) -> IFilterSingle | ModelType:
        if check is None:
            check = {}
        if check_list is None:
            check_list = []
        query = self.get_query.filter(id=object_id)
        if check_list:
            query = query.filter(*check_list)
        if check:
            query = query.filter(**check)
        if load_related:
            query = query.prefetch_related(
                *self.get_related, *self.get_related_backward
            )

        query = query.order_by("-id")
        raw_result = await query.first()

        if not raw_result and raise_error:
            raise get_error_response(
                detail=f"{self.model_name} does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        elif not raw_result:
            return raw_result
        if object_only:
            return raw_result
        if load_related:
            results = await self.to_dict(raw_result=[raw_result])
            if len(results) > 0:
                raw_result = results.pop(0)
        else:
            raw_result = dict(raw_result)
        return IFilterSingle(data=raw_result, status=200)

    async def to_dict(self, raw_result: list[Model]) -> list[dict]:
        columns = (*self.get_related, *self.get_related_backward)
        return [
            {
                **{
                    field_name: [
                        dict(data) for data in list(getattr(result, field_name))
                    ]
                    for field_name in self.model._meta.m2m_fields
                    if hasattr(result, field_name)
                },
                **{
                    field_name: dict(getattr(result, field_name))
                    for field_name in self.model._meta.fk_fields
                    if hasattr(result, field_name) and getattr(result, field_name)
                },
                **{
                    field_name: dict(getattr(result, field_name, {}))
                    for field_name in self.model._meta.o2o_fields
                    if hasattr(result, field_name) and getattr(result, field_name)
                },
                **{
                    attr: getattr(result, attr)
                    for attr in self.model._meta.fields
                    if not attr in columns and not attr.startswith("_")
                },
            }
            for result in raw_result
        ]

    async def filter_and_list(
        self,
        check: dict = None,
        check_list: tuple = None,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "id",
        sort_by: SortEnum = SortEnum.DESC,
        load_related: bool = False,
        total_count: int = None,
        select: str = None,
        object_only: bool = False,
        export_to_excel: bool = False,
        fetch_distinct: bool = False,
    ) -> IFilterList | list[ModelType] | StreamingResponse:
        if check is None:
            check = {}
        query = self.get_query
        if check_list:
            query = query.filter(*check_list)
        if check:
            query = query.filter(**check)
        if fetch_distinct:
            query = query.distinct()
        if not check or check_list:
            query = query.all()

        if load_related and self.get_related:
            query = query.prefetch_related(*self.get_related)
        if sort_by == SortEnum.ASC and order_by:
            query = query.order_by(
                *[
                    f"{col.strip()}"
                    for col in order_by.split(",")
                    if col in self.model._meta.fields
                ]
            )
        elif sort_by == SortEnum.DESC:
            query = query.order_by(
                *[
                    f"-{col.strip()}"
                    for col in order_by.split(",")
                    if col in self.model._meta.fields
                ]
            )
        else:
            query = query.order_by("-id")
        query = query.offset((page - 1) * per_page).limit(per_page)
        if select:
            query = query.values(
                *[
                    col.strip()
                    for col in select.split(",")
                    if col.strip() in self.model._meta.fields
                    and col.strip() not in self.get_related
                ]
            )
        raw_result = await query
        if object_only:
            return raw_result
        if load_related and raw_result and not select and not export_to_excel:
            raw_result = await self.to_dict(raw_result=raw_result)
        else:
            raw_result = [dict(data) for data in raw_result]
        if export_to_excel:
            return self.write_to_excel(models=raw_result, filename=self.model_name)
        if total_count is None:
            get_count = await self.get_count()
            total_count = get_count.count if get_count else 0
        return IFilterList(
            data=raw_result,
            status=200,
            total_count=total_count,
        )

    async def delete_by_ids(self, object_ids: List[int], check: dict = None) -> int:
        if check is None:
            check = {}
        query = self.get_query
        if check:
            query.filter(**check)
        query = query.filter(id__in=object_ids)
        return await query.delete()

    async def delete_by_id(
        self, object_id: int, raise_error: bool = False
    ) -> ModelType:
        result = await self.get_query.filter(id=object_id).delete()
        if result <= 0:
            if raise_error:
                raise get_error_response(
                    f"{self.model_name} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            else:
                return result
        return result

    async def get_by_ids(self, object_ids: List[uuid.UUID]) -> list[ModelType]:
        return await self.get_query.filter(id__in=object_ids).all()

    async def get(self, id: str, raise_error: bool = False) -> Optional[ModelType]:
        query = self.get_query.filter(id=id)
        obj = await query.first()
        if obj is not None:
            return obj
        if raise_error and not obj:
            raise get_error_response(
                detail=f"{self.model_name} is not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return obj

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[ModelType]:
        return await self.get_query.all().offset(offset).limit(limit)

    async def filter_obj(
        self,
        get_first: bool = False,
        check: dict = None,
        check_list: tuple | set | list = (),
        load_related: bool = False,
        raise_error: bool = False,
    ) -> list[modelType] | modelType:
        if not check:
            check = {}
        query = self.get_query
        if load_related:
            query = query.prefetch_related(
                *self.get_related_backward,
                *self.get_related,
            )
        if get_first:
            result = await query.filter(*check_list, **check).first()
        else:
            result = await query.filter(*check_list, **check).all()
        if not result and raise_error:
            raise get_error_response(
                f"{self.model_name} does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return result

    async def get_count(
        self, check: dict = None, check_list: tuple | list | set = ()
    ) -> ICount:
        if check is None:
            check = {}
        query = self.get_query
        if check_list:
            query = query.filter(*check_list)
        if check:
            query = query.filter(**check)
        result = await query.all().count()
        return ICount(count=result)

    async def create(
        self,
        payload: dict | BaseModel,
        to_dict: bool = False,
    ) -> ModelType:
        data_dict = (
            payload.model_dump(exclude_unset=True)
            if isinstance(payload, BaseModel)
            else payload
        )
        instance: ModelType
        if self.tenant_schema:
            instance = await self.model.create(
                **data_dict,
                tenant_id=self.tenant_schema,
            )
        else:
            instance = await self.model.create(**data_dict)
        return dict(instance) if to_dict else instance

    def generate_excel_content(self, payload: List[ModelType | dict | BaseModel]):
        data: list[dict] = []
        for model in payload:
            if isinstance(model, BaseModel) and model:
                data.append(model.model_dump())
            elif isinstance(model, Model) and model:
                data.append(dict(model))
            else:
                data.append(model)
        wb = openpyxl.Workbook()
        ws = wb.active

        data = orjson.dumps(data)
        data = orjson.loads(data)
        ws.title = self.model_name
        if len(data) > 0:
            ws.append(tuple(data[0].keys()))
        for model in data:
            ws.append(tuple(model.values()))
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        yield from output

    def write_to_excel(
        self, models: List[ModelType | dict | BaseModel], filename: str
    ) -> StreamingResponse:
        filename = f"{filename or self.model_name}.xlsx"
        return StreamingResponse(
            self.generate_excel_content(models),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    async def update(
        self, id: str, payload: BaseModel | dict, check: dict = None
    ) -> ModelType:
        query = self.get_query.filter(id=id)
        if check:
            query = query.filter(**check)
        instance = await query.first()
        item = payload.model_dump() if isinstance(payload, BaseModel) else payload
        if not instance:
            raise get_error_response(
                f"{self.model_name} does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        for key, value in item.items():
            setattr(instance, key, value)
        await instance.save()
        return instance

    async def delete(self, id: str, check: dict = None) -> ModelType:
        if check is None:
            check = {}
        instance = await self.filter_obj(
            check=dict(id=id, **check),
            get_first=True,
            raise_error=True,
        )
        await instance.delete()
        return instance

    async def get_or_create(
        self,
        payload: BaseModel | dict,
        raise_error: bool = False,
        check: dict = None,
    ) -> ModelType:
        data_dict = (
            payload.model_dump(exclude_unset=True)
            if isinstance(payload, BaseModel)
            else payload
        )
        check = check or {}
        check_item = await self.get_query.filter(**check).first()
        if check_item and raise_error:
            raise get_error_response(
                f"{self.model_name} already exists",
                status_code=status.HTTP_409_CONFLICT,
            )
        elif not raise_error and check_item:
            return check_item

        if self.tenant_schema:
            data_dict["tenant_id"] = self.tenant_schema
        check_item = await self.model.create(**data_dict)
        return check_item

    async def bulk_create(
        self,
        instances: List[ModelType],
        batch_size: int = 10,
    ) -> list[ModelType]:
        if self.is_tenant:
            for instance in instances:
                instance.tenant_id = self.tenant_schema
        return await self.model.bulk_create(instances, batch_size=batch_size)

    async def bulk_update(self, instances: List[ModelType]) -> list[ModelType]:
        fields = self.model._meta.fields
        current_columns = set()
        if self.get_related:
            current_columns.update(self.get_related)
        if self.get_related_backward:
            current_columns.update(self.get_related_backward)
        if current_columns:
            for column in current_columns:
                if column in fields:
                    fields.remove(column)

        return await self.model.bulk_update(
            instances,
            fields=fields,
            batch_size=10,
        )

    async def bulk_delete(self, objs: List[ModelType]) -> list[ModelType]:
        ids = [obj.id for obj in objs]
        result = await self.get_query.filter(id__in=ids).delete()
        return objs if result else None


import io
from dataclasses import dataclass
import json
import orjson
from typing import List, TypeVar, Generic
import uuid
from edgy import Model
from edgy import QuerySet
from esmerald.responses import StreamingResponse
from esmerald import status
from pydantic import BaseModel
import openpyxl
from fermerce.lib.utils.base_response import (
    ICount,
    IFilterList,
    IFilterSingle,
    SortEnum,
    get_error_response,
)

from typing import List, Optional

ModelType = TypeVar("ModelType", bound=Model)


@dataclass(slots=True, kw_only=True)
class BaseRepository(Generic[ModelType]):
    model: ModelType | None = None
    model_name: str = "Object"

    def make_slug(self, name: str, random_length: Optional[int] = 10) -> str:
        slug = self._clean_string(name)
        slug = slug[:30]
        random_suffix = self._generate_random_suffix(random_length)
        return f"{slug}-{random_suffix}"

    def _clean_string(self, s: str) -> str:
        s = s.lower()
        s = re.sub(r"[\s_]+", "-", s)
        s = re.sub(r"[^\w-]", "", s)
        s = s.strip("-")
        return s

    def _generate_random_suffix(self, length: Optional[int] = 10) -> str:
        if length is None or length < 1:
            length = 10
        elif length > 32:
            length = 32
        return uuid.uuid4().hex[:length].lower()

    def __init__(self):
        self._related_fields: Optional[set[str]] = None
        self._related_backward_fields: Optional[set[str]] = None
        self._model_fields: Optional[set[str]] = None

    @property
    def get_related(self) -> set[str]:
        if self._related_fields is None:
            self._related_fields = set(self.model.meta.foreign_key_fields.keys())
        return self._related_fields

    @property
    def get_related_backward(self) -> set[str]:
        if self._related_backward_fields is None:
            self._related_backward_fields = set(self.model.meta.model_references.keys())
        return self._related_backward_fields

    @property
    def get_fields(self) -> set[str]:
        if self._model_fields is None:
            self._model_fields = set(
                key
                for key in self.model.meta.fields.keys()
                if key not in (*self.get_related_backward, *self.get_related)
            )
        return self._model_fields

    async def to_dict(self, raw_result: List[ModelType]) -> list[dict[str, Any]]:
        return [
            {
                **{
                    field_name: [dict(data) for data in getattr(result, field_name)]
                    for field_name in self.get_related
                    if hasattr(result, field_name)
                },
                **{
                    field_name: dict(getattr(result, field_name))
                    for field_name in self.get_related_backward
                    if hasattr(result, field_name) and getattr(result, field_name)
                },
                **{
                    attr: getattr(result, attr)
                    for attr in self.get_fields
                    if not attr.startswith("_")
                },
            }
            for result in raw_result
        ]

    def _build_query(
        self,
        base_query: QuerySet[ModelType],
        check: dict[str, Any] = None,
        check_list: List[Any] = None,
        load_related: bool = False,
        order_by: str = "-id",
    ) -> QuerySet[ModelType]:
        if check_list:
            base_query = base_query.filter(*check_list)
        if check:
            base_query = base_query.filter(**check)
        if load_related:
            base_query = base_query.prefetch_related(
                *self.get_related, *self.get_related_backward
            )
        return base_query.order_by(order_by)

    @property
    def query(self) -> QuerySet[ModelType]:
        return self.model.query

    async def get_single(
        self,
        object_id: str,
        check: dict[str, Any] = None,
        check_list: list[Any] = None,
        load_related: bool = False,
        raise_error: bool = True,
        object_only: bool = False,
    ) -> IFilterSingle | ModelType:
        query = self._build_query(
            base_query=self.query.filter(id=object_id),
            check=check,
            check_list=check_list,
            load_related=load_related,
        )
        raw_result = await query.first()
        if not raw_result:
            if raise_error:
                raise get_error_response(
                    detail=f"{self.model_name} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return raw_result

        if object_only:
            return raw_result

        if load_related:
            results = await self.to_dict([raw_result])
            raw_result = results[0] if results else {}
        else:
            raw_result = dict(raw_result)
        return IFilterSingle(data=raw_result, status=200)

    def _build_base_query(
        self, check: dict = None, check_list: tuple = None, fetch_distinct: bool = False
    ) -> QuerySet:
        query = self.query
        if check_list:
            query = query.filter(*check_list)
        if check:
            query = query.filter(**check)
        if fetch_distinct:
            query = query.distinct("id")
        return query.all()

    def _apply_sorting(
        self, query: QuerySet, order_by: str, sort_by: SortEnum
    ) -> QuerySet:
        if order_by:
            valid_fields = self.model.meta.fields.keys()
            order_fields = [
                f"{'-' if sort_by == SortEnum.DESC else ''}{col.strip()}"
                for col in order_by.split(",")
                if col.strip() in valid_fields.keys()
            ]
            if order_fields:
                return query.order_by(*order_fields)
        return query.order_by("-id")

    def _apply_pagination(self, query: QuerySet, page: int, per_page: int) -> QuerySet:
        return query.offset((page - 1) * per_page).limit(per_page)

    def _apply_select(self, query: QuerySet, select: str) -> QuerySet:
        if select:
            valid_fields = set(self.model.meta.fields.keys()) - set(self.get_related)
            select_fields = [
                col.strip() for col in select.split(",") if col.strip() in valid_fields
            ]
            if select_fields:
                return query.values(*select_fields)
        return query

    async def _process_result(
        self, raw_result: list, load_related: bool, select: str, export_to_excel: bool
    ) -> list:
        if load_related and raw_result and not select and not export_to_excel:
            return await self.to_dict(raw_result=raw_result)
        return [dict(data) for data in raw_result]

    async def _get_total_count(
        self, total_count: int, check: dict, check_list: tuple
    ) -> int:
        if not total_count:
            get_count = await self.get_count(check=check, check_list=check_list)
            return get_count.count if get_count else 0
        return total_count

    async def delete_by_ids(
        self, object_ids: List[int], check: Optional[dict] = None
    ) -> int:
        query = self._build_delete_query(object_ids, check)
        return await query.delete()

    async def delete_by_id(
        self, object_id: int, raise_error: bool = False
    ) -> Optional[int]:
        query = self.query.filter(id=object_id)
        result = await query.delete()

        if result <= 0 and raise_error:
            raise self._get_not_found_error()

        return result if result > 0 else None

    async def get_by_ids(self, object_ids: List[uuid.UUID]) -> List[ModelType]:
        query = self.query.filter(id__in=object_ids)
        return await query.all()

    def _build_delete_query(
        self, object_ids: List[int], check: Optional[dict] = None
    ) -> QuerySet:
        query = self.query.filter(id__in=object_ids)
        if check:
            query = query.filter(**check)
        return query

    def _get_not_found_error(self):
        return get_error_response(
            f"{self.model_name} does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async def get(self, id: str, raise_error: bool = False) -> Optional[ModelType]:
        obj = await self.query.filter(id=id).first()
        if obj is None and raise_error:
            raise self._get_not_found_error()
        return obj

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[ModelType]:
        query = self._build_get_all_query(limit, offset)
        return await query

    def _build_get_all_query(self, limit: int, offset: int) -> QuerySet[ModelType]:
        return self.query.all().offset(offset).limit(limit)

    async def filter_obj(
        self,
        get_first: bool = False,
        check: Optional[Dict[str, Any]] = None,
        check_list: Union[tuple, set, list] = (),
        load_related: bool = False,
        raise_error: bool = False,
    ) -> Union[List[ModelType], ModelType, None]:
        query = self._build_filter_query(check, check_list, load_related)

        if get_first:
            result = await query.first()
        else:
            result = await query.all()
        if not result and raise_error:
            raise self._get_not_found_error()
        return result

    async def get_count(
        self,
        check: Optional[Dict[str, Any]] = None,
        check_list: Union[tuple, list, set] = (),
    ) -> ICount:
        query = self._build_count_query(check, check_list)
        result = await query.count()
        return ICount(count=result)

    async def create(
        self,
        payload: Union[dict, BaseModel],
        to_dict: bool = False,
    ) -> Union[ModelType, Dict[str, Any]]:
        data_dict = self._prepare_create_data(payload)
        instance = await self.query.create(**data_dict)
        return dict(instance) if to_dict else instance

    def _build_filter_query(
        self,
        check: Optional[Dict[str, Any]],
        check_list: Union[tuple, set, list],
        load_related: bool,
    ) -> QuerySet[ModelType]:
        query = self.query
        if load_related:
            query = query.prefetch_related(
                *self.get_related_backward, *self.get_related
            )
        return query.filter(*check_list, **(check or {}))

    def _build_count_query(
        self, check: Optional[Dict[str, Any]], check_list: Union[tuple, list, set]
    ) -> QuerySet[ModelType]:
        query = self.query
        if check_list:
            query = query.filter(*check_list)
        if check:
            query = query.filter(**check)
        return query

    def _prepare_create_data(self, payload: Union[dict, BaseModel]) -> Dict[str, Any]:
        if isinstance(payload, BaseModel):
            return payload.model_dump(exclude_unset=True)
        return payload

    def generate_excel_content(
        self, payload: List[Union[ModelType, Dict[str, Any], BaseModel]]
    ) -> Generator[bytes, None, None]:
        data = self._prepare_excel_data(payload)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.model_name

        if data:
            ws.append(tuple(data[0].keys()))
            for row in data:
                ws.append(tuple(row.values()))

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        yield from output

    def write_to_excel(
        self,
        models: List[Union[ModelType, Dict[str, Any], BaseModel]],
        filename: Optional[str] = None,
    ) -> StreamingResponse:
        filename = f"{filename or self.model_name}.xlsx"
        return StreamingResponse(
            self.generate_excel_content(models),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    def _prepare_excel_data(
        self, payload: List[Union[ModelType, Dict[str, Any], BaseModel]]
    ) -> List[Dict[str, Any]]:
        data = []
        for item in payload:
            if isinstance(item, BaseModel):
                data.append(item.model_dump())
            elif isinstance(item, Model):
                data.append(dict(item))
            else:
                data.append(item)
        return orjson.loads(orjson.dumps(data))

    async def update(
        self,
        id: str,
        payload: Union[BaseModel, Dict[str, Any]],
        check: Optional[Dict[str, Any]] = None,
    ) -> ModelType:
        query = self._build_update_query(id, check)
        instance = await self._get_instance_for_update(query)

        data = self._prepare_update_data(payload)
        await self._apply_updates(instance, data)

        return instance

    async def delete(
        self, id: str, check: Optional[Dict[str, Any]] = None
    ) -> ModelType:
        instance = await self.filter_obj(
            check=dict(id=id, **(check or {})),
            get_first=True,
            raise_error=True,
        )
        async with self.model.connection():
            await instance.delete()
        return instance

    async def get_or_create(
        self,
        payload: Union[BaseModel, Dict[str, Any]],
        raise_error: bool = False,
        check: Optional[Dict[str, Any]] = None,
    ) -> ModelType:
        check = check or {}
        data_dict = self._prepare_create_data(payload)

        async with self.model.connection():
            check_item = await self.query.filter(**check).first()
            if check_item:
                if raise_error:
                    raise self._get_already_exists_error()
                return check_item
            return await self.query.create(**data_dict)

    async def bulk_create(self, instances: List[Dict[str, Any]]) -> List[ModelType]:
        async with self.model.connection():
            return await self.query.bulk_create(instances)

    async def bulk_update(self, instances: List[ModelType]) -> List[ModelType]:
        fields = self._get_updateable_fields()
        async with self.model.connection():
            return await self.query.bulk_update(instances, fields=fields)

    async def bulk_delete(self, objs: List[ModelType]) -> Optional[List[ModelType]]:
        ids = [obj.id for obj in objs]
        async with self.model.connection():
            result = await self.query.filter(id__in=ids).delete()
        return objs if result else None

    def _build_update_query(
        self, id: str, check: Optional[Dict[str, Any]]
    ) -> QuerySet[ModelType]:
        query = self.query.filter(id=id)
        if check:
            query = query.filter(**check)
        return query

    async def _get_instance_for_update(self, query: QuerySet[ModelType]) -> ModelType:
        async with self.model.connection():
            instance = await query.first()
        if not instance:
            raise self._get_not_found_error()
        return instance

    def _prepare_update_data(
        self, payload: Union[BaseModel, Dict[str, Any]]
    ) -> Dict[str, Any]:
        return payload.model_dump() if isinstance(payload, BaseModel) else payload

    async def _apply_updates(self, instance: ModelType, data: Dict[str, Any]):
        for key, value in data.items():
            setattr(instance, key, value)
        async with self.model.connection():
            await instance.save()

    def _get_updateable_fields(self) -> List[str]:
        fields = set(self.model.meta.fields.keys())
        related_fields = self.get_related | self.get_related_backward
        return list(fields - related_fields)

    def _get_already_exists_error(self):
        return get_error_response(
            f"{self.model_name} already exists",
            status_code=status.HTTP_409_CONFLICT,
        )
