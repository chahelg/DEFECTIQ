"""Authentication service layer."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password, verify_token
from app.repositories.user_repository import UserRepository
from app.schemas import LoginRequest, RefreshTokenRequest, TokenResponse, UserCreate, UserResponse


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, payload: UserCreate) -> UserResponse:
        if await self.user_repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        if await self.user_repository.get_by_username(payload.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        user = await self.user_repository.create(
            {
                "email": payload.email,
                "username": payload.username,
                "full_name": payload.full_name,
                "department": payload.department,
                "role": payload.role,
                "hashed_password": hash_password(payload.password),
                "is_active": True,
            }
        )
        return UserResponse.model_validate(user)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        user.last_login = datetime.now(timezone.utc)
        await self.user_repository.session.commit()

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=30 * 60)

    async def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        token_payload = verify_token(payload.refresh_token)
        if token_payload.get("token_type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = await self.user_repository.get_by_id(token_payload.get("sub"))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            expires_in=30 * 60,
        )

    async def current_user(self, user_id: str) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.model_validate(user)