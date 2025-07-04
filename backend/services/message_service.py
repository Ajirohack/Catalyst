"""Message Service

This module defines the message service for managing conversation messages.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Message
from database.repository import MessageRepository
from services.base import BaseService
from services.session_service import SessionService


class MessageService(BaseService):
    """Service for message operations including processing and scoring."""

    def __init__(self, db: AsyncSession):
        """Initialize message service with database session."""
        super().__init__(MessageRepository(Message, db))
        self.db = db
        self.session_service = SessionService(db)

    async def create_message(
        self,
        session_id: Union[UUID, str],
        sender: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Create a new message."""
        message_data = {
            "session_id": session_id,
            "sender": sender,
            "text": text,
            "metadata_": metadata or {},
        }
        return await self.create(obj_in=message_data)

    async def get_session_messages(
        self,
        session_id: Union[UUID, str],
        skip: int = 0,
        limit: int = 100,
        order_by_desc: bool = True,
    ) -> List[Message]:
        """Get messages for a specific session."""
        return await self.repository.get_session_messages(
            session_id=session_id, skip=skip, limit=limit, order_by_desc=order_by_desc
        )

    async def process_user_message(
        self,
        session_id: Union[UUID, str],
        user_id: Union[UUID, str],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Process a message from the user and return Diego's response."""
        # 1. Save the user's message
        user_message = await self.create_message(
            session_id=session_id, sender="user", text=text, metadata=metadata
        )

        # 2. Get the session to check stage and scores
        session = await self.session_service.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 3. Analyze the message and generate a response
        # TODO: Implement more sophisticated message analysis
        analysis = self._analyze_message(text)

        # 4. Update session scores based on message analysis
        await self.session_service.update_session_scores(
            session_id=session_id,
            trust_delta=analysis.get("trust_delta", 0.0),
            openness_delta=analysis.get("openness_delta", 0.0),
        )

        # 5. Generate Diego's response based on the current stage and message
        response_text = self._generate_response(
            user_message=text, stage=session.current_stage, analysis=analysis
        )

        # 6. Save and return Diego's response
        return await self.create_message(
            session_id=session_id,
            sender="diego",
            text=response_text,
            metadata={
                "analysis": analysis,
                "stage": session.current_stage,
                "is_ai_generated": True,
            },
        )

    def _analyze_message(self, text: str) -> Dict[str, Any]:
        """Analyze a message and return insights."""
        # TODO: Implement more sophisticated analysis
        # This is a placeholder implementation
        word_count = len(text.split())
        char_count = len(text)

        # Simple sentiment analysis (placeholder)
        sentiment = 0.5  # Neutral
        if any(word in text.lower() for word in ["happy", "great", "awesome"]):
            sentiment = 0.8
        elif any(word in text.lower() for word in ["sad", "bad", "terrible"]):
            sentiment = 0.2

        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentiment": sentiment,
            "trust_delta": 0.1,  # Small increase in trust for any message
            "openness_delta": (
                0.05 if word_count > 5 else 0.02
            ),  # Reward longer messages
        }

    def _generate_response(
        self, user_message: str, stage: str, analysis: Dict[str, Any]
    ) -> str:
        """Generate a response based on the user's message and current stage."""
        # TODO: Implement more sophisticated response generation
        # This is a placeholder implementation

        # Simple keyword matching for demo purposes
        user_message_lower = user_message.lower()

        if any(word in user_message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! How can I help you today?"

        if any(
            word in user_message_lower for word in ["how are you", "how's it going"]
        ):
            return (
                "I'm just a computer program, but I'm functioning well. How about you?"
            )

        if any(word in user_message_lower for word in ["thank", "thanks"]):
            return "You're welcome! Is there anything else you'd like to discuss?"

        # Default response based on stage
        if stage == "APP":
            return "I appreciate you sharing that. Could you tell me more about what brings you here today?"
        elif stage == "FPP":
            return "That's interesting. How does that make you feel?"
        else:  # RPP
            return "Thank you for being so open with me. What are your thoughts on how we can move forward?"
