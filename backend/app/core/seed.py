"""Bootstrap helpers for local development."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User


async def seed_demo_data(session: AsyncSession) -> None:
    user_count = await session.scalar(select(func.count()).select_from(User))

    if not user_count:
        session.add(
            User(
                email="admin@defectiq.com",
                hashed_password=hash_password("Admin@123"),
                full_name="Admin User",
                role="admin",
                is_active=True,
            )
        )
    await session.commit()