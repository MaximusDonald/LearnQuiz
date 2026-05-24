"""Pydantic schemas for authentication endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    """Payload for email/password registration."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    """Payload for email/password login."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Payload used to renew an access token."""

    refresh_token: str = Field(min_length=20)


class TokenResponse(BaseModel):
    """Pair of JWTs returned after authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    """Serializable authenticated user profile."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    google_id: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    """Full authentication response with tokens and user profile."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
