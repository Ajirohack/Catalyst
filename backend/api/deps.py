"""API Dependencies

This module defines FastAPI dependencies for authentication and service injection.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.base import get_db
from database.models import User
from services.user_service import UserService

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current user and verify admin role."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# Dependency to get the current user service
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get an instance of UserService with database session."""
    return UserService(db)


# Dependency to get the current session service
def get_session_service(db: AsyncSession = Depends(get_db)) -> "SessionService":
    """Get an instance of SessionService with database session."""
    from services.session_service import SessionService

    return SessionService(db)


# Dependency to get the current message service
def get_message_service(db: AsyncSession = Depends(get_db)) -> "MessageService":
    """Get an instance of MessageService with database session."""
    from services.message_service import MessageService

    return MessageService(db)


# Dependency to get the current template service
def get_template_service(db: AsyncSession = Depends(get_db)) -> "TemplateService":
    """Get an instance of TemplateService with database session."""
    from services.template_service import TemplateService

    return TemplateService(db)
