"""Session Service

This module defines the session service for managing user conversation sessions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Session
from database.repository import SessionRepository
from services.base import BaseService


class SessionService(BaseService):
    """Service for session operations."""

    def __init__(self, db: AsyncSession):
        """Initialize session service with database session."""
        super().__init__(SessionRepository(Session, db))
        self.db = db

    async def get_user_sessions(
        self,
        user_id: Union[UUID, str],
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Session]:
        """Get all sessions for a specific user."""
        return await self.repository.get_user_sessions(
            user_id=user_id, active_only=active_only, skip=skip, limit=limit
        )

    async def get_with_messages(
        self, session_id: Union[UUID, str], limit: int = 100
    ) -> Optional[Session]:
        """Get a session with its messages."""
        return await self.repository.get_with_messages(
            session_id=session_id, limit=limit
        )

    async def create_session(
        self,
        user_id: Union[UUID, str],
        title: str = "New Conversation",
        metadata_: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session for a user."""
        session_data = {
            "user_id": user_id,
            "title": title,
            "current_stage": "APP",
            "scores": {"trust": 0.0, "openness": 0.0},
            "flags": {},
            "metadata_": metadata_ or {},
            "is_active": True,
        }
        return await self.create(obj_in=session_data)

    async def update_session_scores(
        self,
        session_id: Union[UUID, str],
        trust_delta: float = 0.0,
        openness_delta: float = 0.0,
    ) -> Optional[Session]:
        """Update session scores with deltas."""
        session = await self.get(session_id)
        if not session:
            return None

        # Update scores with bounds checking
        new_trust = max(
            0.0, min(100.0, (session.scores.get("trust", 0.0) + trust_delta))
        )
        new_openness = max(
            0.0, min(100.0, (session.scores.get("openness", 0.0) + openness_delta))
        )

        # Check for stage transitions
        current_stage = session.current_stage
        new_stage = current_stage

        if current_stage == "APP" and new_trust >= 60 and new_openness >= 40:
            new_stage = "FPP"
        elif current_stage == "FPP" and new_trust >= 75 and new_openness >= 60:
            new_stage = "RPP"

        update_data = {
            "scores": {"trust": new_trust, "openness": new_openness},
            "current_stage": new_stage,
        }

        return await self.update(session_id, update_data)

    async def close_session(self, session_id: Union[UUID, str]) -> bool:
        """Mark a session as inactive."""
        result = await self.update(
            session_id, {"is_active": False, "ended_at": datetime.utcnow()}
        )
        return result is not None

    async def get_active_session_count(self, user_id: Union[UUID, str]) -> int:
        """Get the number of active sessions for a user."""
        sessions = await self.get_user_sessions(user_id, active_only=True)
        return len(sessions)
