"""Seed the DefectIQ local PostgreSQL database with demo data."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys
from random import choice, randint

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

BACKEND_DIR = Path(__file__).resolve().parents[1] / 'backend'
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import Settings
from app.core.database import Base
from app.core.security import hash_password
from app.ml.model_manager import ModelManager
from app.models import Defect, User


def get_settings() -> Settings:
    env_file = Path(__file__).resolve().parents[1] / "backend" / ".env"
    return Settings(_env_file=env_file, _env_file_encoding="utf-8")


async def seed() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    priorities = ["Critical", "High", "Medium", "Low"]
    statuses = ["Open", "In Progress", "Resolved", "Closed", "Reopened"]
    categories = ["Access", "Payments", "UI", "Integrations", "Performance", "Data", "Security"]
    assignees = ["A. Kumar", "S. Patel", "L. Chen", "M. Rivera", "J. Wilson", "T. Brown"]

    async with session_factory() as session:
        admin = await session.scalar(select(User).where(User.email == "admin@defectiq.com"))
        if admin is None:
            session.add(
                User(
                    email="admin@defectiq.com",
                    hashed_password=hash_password("Admin@123"),
                    full_name="DefectIQ Admin",
                    role="admin",
                    is_active=True,
                )
            )

        existing_numbers = set((await session.execute(select(Defect.number))).scalars().all())
        now = datetime.now(UTC)
        rows: list[Defect] = []

        for index in range(50):
            number = f"DEF-{1000 + index}"
            if number in existing_numbers:
                continue

            opened_at = now - timedelta(days=randint(1, 120), hours=randint(0, 23))
            status = choice(statuses)
            resolved_at = opened_at + timedelta(hours=randint(2, 220)) if status in {"Resolved", "Closed"} else None
            sla_due = opened_at + timedelta(hours=randint(24, 96))
            breached = bool(resolved_at and resolved_at > sla_due) or (status in {"Open", "In Progress", "Reopened"} and sla_due < now)

            rows.append(
                Defect(
                    number=number,
                    title=f"Sample defect {index + 1}",
                    description=f"Generated sample defect record {index + 1}",
                    priority=choice(priorities),
                    status=status,
                    category=choice(categories),
                    assigned_to=choice(assignees),
                    opened_at=opened_at,
                    resolved_at=resolved_at,
                    sla_due=sla_due,
                    is_sla_breached=breached,
                    reopen_count=randint(0, 3),
                    is_deleted=False,
                )
            )

        if rows:
            await session.execute(
                insert(Defect),
                [
                    {
                        "number": row.number,
                        "title": row.title,
                        "description": row.description,
                        "priority": row.priority,
                        "status": row.status,
                        "category": row.category,
                        "assigned_to": row.assigned_to,
                        "opened_at": row.opened_at,
                        "resolved_at": row.resolved_at,
                        "sla_due": row.sla_due,
                        "is_sla_breached": row.is_sla_breached,
                        "reopen_count": row.reopen_count,
                        "is_deleted": row.is_deleted,
                    }
                    for row in rows
                ],
            )

        await session.commit()
        await ModelManager.train_all(session)

    await engine.dispose()
    print("Seed complete: admin user ensured, sample defects inserted, and Phase 2 models prepared.")


if __name__ == "__main__":
    asyncio.run(seed())