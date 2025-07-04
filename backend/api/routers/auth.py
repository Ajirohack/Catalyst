from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from config import settings
from database.base import get_db
from database.models import User
from services.user_service import UserService
from api.schemas.auth import (
    Token,
    UserCreate,
    UserResponse,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from api.deps import get_user_service, get_current_active_user

router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "message": "Auth router is working"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user.

    - **email**: User's email address (must be unique)
    - **username**: Username (must be unique, 3-50 chars, alphanumeric + _-)
    - **password**: Password (min 8 chars, must include upper, lower, number)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    # Check if user with this email already exists
    existing_user = await user_service.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username is taken
    existing_username = await user_service.get_by_username(user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create the user
    user = await user_service.create_user(user_in.dict())

    # Log the user in by generating a token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = user_service.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    # Update last login
    await user_service.update_last_login(user.id)

    # Return user data with token
    user_dict = user.__dict__.copy()
    user_dict["access_token"] = token
    user_dict["token_type"] = "bearer"
    user_dict["expires_in"] = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return user_dict


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.

    - **username**: Username or email
    - **password**: Password
    """
    import logging
    from fastapi import Request
    from fastapi.routing import APIRoute

    # Debug logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Log the incoming request details
    logger.debug(f"Login attempt - Username: {form_data.username}")
    logger.debug(f"Form data: {form_data.__dict__}")

    # Authenticate user
    user = await user_service.authenticate_user(
        username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_service.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    # Update last login
    await user_service.update_last_login(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/password-reset/request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Request a password reset.

    - **email**: User's email address
    """
    # Check if user exists
    user = await user_service.get_by_email(reset_request.email)
    if not user:
        # Don't reveal that the email doesn't exist
        return {
            "message": "If your email is registered, you will receive a password reset link"
        }

    # Generate a reset token (valid for 1 hour)
    reset_token = user_service.create_access_token(
        subject=str(user.id), expires_delta=timedelta(hours=1)
    )

    # TODO: Send email with reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    # In a real app, you would send an email here
    print(f"Password reset link for {user.email}: {reset_link}")

    return {
        "message": "If your email is registered, you will receive a password reset link"
    }


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Confirm password reset with token.

    - **token**: Password reset token
    - **new_password**: New password
    """
    try:
        # Verify the reset token
        payload = jwt.decode(
            reset_confirm.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
            )

        # Get the user
        user = await user_service.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update the password
        hashed_password = user_service.get_password_hash(reset_confirm.new_password)
        await user_service.update(user.id, {"hashed_password": hashed_password})

        return {"message": "Password updated successfully"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user information.

    Returns the currently authenticated user's data.
    """
    return current_user
