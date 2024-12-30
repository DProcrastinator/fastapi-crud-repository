from fastapi import HTTPException
from typing import Generic, Type, TypeVar, Optional , Dict ,Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeMeta , selectinload
from fastapi_pagination import Params, Page
from sqlalchemy.sql.expression import or_
from sqlalchemy import asc, desc
from fastapi_pagination.ext.sqlalchemy import paginate


# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
SchemaType = TypeVar("SchemaType")

class BaseRepository(Generic[ModelType, SchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, schema: SchemaType) -> ModelType:
        """Create a new record."""
        new_record = self.model(**schema.model_dump())
        self.db.add(new_record)
        await self.db.commit()
        await self.db.refresh(new_record)
        return new_record

    async def get(self, record_id: int, load_relations: list[str] = None) -> Optional[ModelType]:
        """Get a record by its ID."""
        query = select(self.model).filter_by(id=record_id)
        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(getattr(self.model, relation)))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        """Get all records."""
        query = await self.db.execute(select(self.model))
        return query.scalars().all()

    async def update(self, record_id: int, schema: SchemaType) -> Optional[ModelType]:
        """Update a record."""
        query = await self.db.execute(select(self.model).filter_by(id=record_id))
        record = query.scalar_one_or_none()
        if not record:
            return None
        for key, value in schema.dict(exclude_unset=True).items():
            setattr(record, key, value)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def delete(self, record_id: int) -> bool:
        """Delete a record."""
        query = await self.db.execute(select(self.model).filter_by(id=record_id))
        record = query.scalar_one_or_none()
        if not record:
            return False
        await self.db.delete(record)
        await self.db.commit()
        return True

    async def index(
            self,
            params: Params,
            filters: Optional[Dict[str, Any]] = None,
            search_fields: Optional[list[str]] = None,
            search_query: Optional[str] = None,
            sort_field: Optional[str] = None,
            sort_order: str = "desc",
            load_relations: list[str] = None
            ) -> Page[ModelType]:
        query = select(self.model)
        #apply filters:
        if filters:
            for field,value in filters:
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)
        #apply search
        if search_query and search_fields:
            search_conditions = [
                getattr(self.model, field).ilike(f"%{search_query}%")
                for field in search_fields
                if hasattr(self.model, field)
            ]
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        #apply sorting
        if sort_field and hasattr(self.model, sort_field):
            order_func = asc if sort_order.lower()== 'asc' else desc
            query = query.order_by(order_func(getattr(self.model, sort_field)))
        else:
            query = query.order_by(desc(self.model.id))

        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(getattr(self.model, relation)))


        return await paginate(self.db , query, params)










