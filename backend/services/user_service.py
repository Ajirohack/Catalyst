"""User Service

This module defines the user service for authentication and user management.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.models import User
from database.repository import UserRepository
from services.base import BaseService

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService):
    """Service for user operations including authentication."""

    def __init__(self, db: AsyncSession):
        """Initialize user service with database session."""
        super().__init__(UserRepository(User, db))
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return await self.repository.get_by_username(username)

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user with hashed password."""
        # Check if user with this email already exists
        existing_user = await self.get_by_email(user_data["email"])
        if existing_user:
            raise ValueError("User with this email already exists")

        # Check if username is taken
        existing_username = await self.get_by_username(user_data["username"])
        if existing_username:
            raise ValueError("Username already taken")

        # Hash the password
        hashed_password = self.get_password_hash(user_data["password"])

        # Create user data
        user_dict = {
            "email": user_data["email"],
            "username": user_data["username"],
            "hashed_password": hashed_password,
            "is_active": True,
        }

        # Add any additional fields
        for field in ["first_name", "last_name"]:
            if field in user_data:
                user_dict[field] = user_data[field]

        return await self.create(obj_in=user_dict)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username/email and password."""
        # Try to get user by username or email
        user = await self.get_by_username(username)
        if not user:
            user = await self.get_by_email(username)

        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        return user

    def create_access_token(
        self, subject: Union[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate a password hash."""
        return pwd_context.hash(password)

    async def update_last_login(self, user_id: Union[UUID, str]) -> None:
        """Update the user's last login timestamp."""
        await self.update(user_id, {"last_login": datetime.utcnow()})
