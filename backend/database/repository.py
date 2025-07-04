"""Database Repository Classes

This module defines repository classes for database operations.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Union[UUID, str]) -> Optional[ModelType]:
        """Get a single record by ID."""
        if isinstance(id, str):
            id = UUID(id)
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> List[ModelType]:
        """Get multiple records with optional filtering and pagination."""
        query = select(self.model)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)  # type: ignore
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, id: Union[UUID, str], obj_in: Dict[str, Any], exclude_unset: bool = False
    ) -> Optional[ModelType]:
        """Update a record."""
        if isinstance(id, str):
            id = UUID(id)

        if exclude_unset:
            update_data = {k: v for k, v in obj_in.items() if v is not None}
        else:
            update_data = obj_in

        result = await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )

        updated = result.scalar_one_or_none()
        if updated:
            await self.db.refresh(updated)
        return updated

    async def delete(self, id: Union[UUID, str]) -> bool:
        """Delete a record."""
        if isinstance(id, str):
            id = UUID(id)

        result = await self.db.execute(
            delete(self.model).where(self.model.id == id).returning(self.model.id)
        )
        return result.scalar_one_or_none() is not None


class UserRepository(BaseRepository):
    """Repository for User model with user-specific queries."""

    async def get_by_email(self, email: str) -> Optional[Any]:
        """Get a user by email."""
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[Any]:
        """Get a user by username."""
        result = await self.db.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalar_one_or_none()


class SessionRepository(BaseRepository):
    """Repository for Session model with session-specific queries."""

    async def get_user_sessions(
        self,
        user_id: Union[UUID, str],
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Any]:
        """Get all sessions for a specific user."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        query = select(self.model).where(self.model.user_id == user_id)

        if active_only:
            query = query.where(self.model.is_active == True)  # noqa: E712

        query = query.order_by(self.model.updated_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_with_messages(
        self, session_id: Union[UUID, str], limit: int = 100, order_by_desc: bool = True
    ) -> Optional[Any]:
        """Get a session with its messages."""
        if isinstance(session_id, str):
            session_id = UUID(session_id)

        query = (
            select(self.model)
            .options(selectinload(self.model.messages))
            .where(self.model.id == session_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class MessageRepository(BaseRepository):
    """Repository for Message model with message-specific queries."""

    async def get_session_messages(
        self,
        session_id: Union[UUID, str],
        skip: int = 0,
        limit: int = 100,
        order_by_desc: bool = True,
    ) -> List[Any]:
        """Get messages for a specific session."""
        if isinstance(session_id, str):
            session_id = UUID(session_id)

        query = select(self.model).where(self.model.session_id == session_id)

        if order_by_desc:
            query = query.order_by(self.model.created_at.desc())
        else:
            query = query.order_by(self.model.created_at.asc())

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()


class MessageTemplateRepository(BaseRepository):
    """Repository for MessageTemplate model with template-specific queries."""

    async def get_by_stage(
        self, stage: str, active_only: bool = True, skip: int = 0, limit: int = 100
    ) -> List[Any]:
        """Get templates by stage."""
        query = select(self.model).where(self.model.stage == stage.upper())

        if active_only:
            query = query.where(self.model.is_active == True)  # noqa: E712

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_trigger(
        self, trigger: str, stage: Optional[str] = None, active_only: bool = True
    ) -> List[Any]:
        """Get templates by trigger and optionally by stage."""
        query = select(self.model).where(self.model.trigger == trigger)

        if stage:
            query = query.where(self.model.stage == stage.upper())

        if active_only:
            query = query.where(self.model.is_active == True)  # noqa: E712

        result = await self.db.execute(query)
        return result.scalars().all()
