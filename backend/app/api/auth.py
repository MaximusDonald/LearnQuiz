"""Authentication API routes."""

from urllib.parse import urlencode
from uuid import UUID

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    validate_token_type,
    verify_password,
    hash_password,
)
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def build_auth_response(user: User) -> AuthResponse:
    """Create a complete auth response for a user."""

    return AuthResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
        user=UserProfileResponse.model_validate(user),
    )


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Fetch a user by email."""

    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Create a new local account and return JWT tokens."""

    normalized_email = payload.email.strip().lower()
    existing_user = await get_user_by_email(session, normalized_email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already exists with this email.",
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Authenticate a local user and return JWT tokens."""

    normalized_email = payload.email.strip().lower()
    user = await get_user_by_email(session, normalized_email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return build_auth_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Renew an access token from a valid refresh token."""

    decoded = decode_token(payload.refresh_token)
    user_id: UUID = validate_token_type(decoded, expected_type="refresh")
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@router.get("/me", response_model=UserProfileResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    """Return the profile of the authenticated user."""

    return UserProfileResponse.model_validate(current_user)


@router.get("/google")
async def google_login(request: Request) -> RedirectResponse:
    """Redirect the user to Google's OAuth consent screen."""

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured.",
        )

    redirect_uri = f"{settings.BACKEND_URL}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Handle the Google OAuth callback and issue local JWT tokens."""

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured.",
        )

    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if user_info is None:
        user_info = await oauth.google.userinfo(token=token)

    google_id = user_info.get("sub")
    email = user_info.get("email")
    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not return the required profile fields.",
        )

    normalized_email = email.strip().lower()
    query = select(User).where(
        or_(User.google_id == google_id, User.email == normalized_email),
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=normalized_email,
            google_id=google_id,
            full_name=user_info.get("name"),
            avatar_url=user_info.get("picture"),
        )
        session.add(user)
    else:
        user.google_id = user.google_id or google_id
        user.full_name = user.full_name or user_info.get("name")
        user.avatar_url = user_info.get("picture") or user.avatar_url

    await session.commit()
    await session.refresh(user)

    auth_response = build_auth_response(user)
    redirect_query = urlencode(
        {
            "access_token": auth_response.access_token,
            "refresh_token": auth_response.refresh_token,
        },
    )
    redirect_url = f"{settings.FRONTEND_URL}/auth/google/callback?{redirect_query}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
