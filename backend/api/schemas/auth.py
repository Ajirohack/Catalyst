"""Authentication Schemas

This module defines Pydantic models for authentication-related API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class Token(BaseModel):
    """JWT token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data model."""

    user_id: Optional[str] = None


class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserUpdate(BaseModel):
    """User update model."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$"
    )
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User model for database operations."""

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserResponse(UserInDB):
    """User response model (without sensitive data)."""

    pass


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str


class PasswordResetRequest(BaseModel):
    """Password reset request model."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v
