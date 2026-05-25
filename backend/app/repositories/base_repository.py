"""Base repository class with common async CRUD operations."""

from __future__ import annotations

import logging
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(self, obj_data: dict[str, Any]) -> T:
        obj = self.model(**obj_data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        logger.debug("Created %s with id %s", self.model.__name__, getattr(obj, "id", None))
        return obj

    async def get_by_id(self, id: str | UUID) -> T | None:
        statement = select(self.model).where(self.model.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update(self, id: str | UUID, obj_data: dict[str, Any]) -> T | None:
        obj = await self.get_by_id(id)
        if obj is None:
            return None

        for key, value in obj_data.items():
            if hasattr(obj, key) and value is not None:
                setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        logger.debug("Updated %s with id %s", self.model.__name__, id)
        return obj

    async def delete(self, id: str | UUID) -> bool:
        obj = await self.get_by_id(id)
        if obj is None:
            return False

        await self.session.delete(obj)
        await self.session.commit()
        logger.debug("Deleted %s with id %s", self.model.__name__, id)
        return True

    async def count(self) -> int:
        statement = select(func.count()).select_from(self.model)
        result = await self.session.execute(statement)
        return int(result.scalar() or 0)

    async def filter_by(self, **kwargs: Any) -> list[T]:
        statement = select(self.model)
        for key, value in kwargs.items():
            if value is not None and hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

