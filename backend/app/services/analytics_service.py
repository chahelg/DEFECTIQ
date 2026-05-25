from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List, Dict, Any


async def backlog_by_assignment_group(db: AsyncSession) -> List[Dict[str, Any]]:
    q = await db.execute(text("SELECT assignment_group, COUNT(*) as backlog FROM defects WHERE closed_at IS NULL GROUP BY assignment_group ORDER BY backlog DESC"))
    rows = q.fetchall()
    return [{'assignment_group': r[0], 'backlog': int(r[1])} for r in rows]


async def defects_older_than(db: AsyncSession, days: int = 7) -> List[Dict[str, Any]]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    q = await db.execute(text("SELECT defect_id, short_description, opened_at FROM defects WHERE closed_at IS NULL AND opened_at < :cutoff"), {'cutoff': cutoff})
    rows = q.fetchall()
    return [{'defect_id': r[0], 'short_description': r[1], 'opened_at': r[2].isoformat() if r[2] else None} for r in rows]


async def trends_by_week(db: AsyncSession, weeks: int = 12):
    q = await db.execute(text("SELECT date_trunc('week', opened_at) as wk, COUNT(*) as cnt FROM defects WHERE opened_at IS NOT NULL GROUP BY wk ORDER BY wk ASC"))
    rows = q.fetchall()
    return [{'week': r[0].isoformat() if r[0] else None, 'count': int(r[1])} for r in rows]
"""Analytics service for trends and operational insights."""

from sqlalchemy import func, select

from app.models import Defect
from app.repositories.defect_repository import DefectRepository


class AnalyticsService:
    def __init__(self, defect_repository: DefectRepository):
        self.defect_repository = defect_repository

    async def by_status(self) -> dict[str, int]:
        result = await self.defect_repository.session.execute(
            select(self.defect_repository.model.status, func.count(self.defect_repository.model.id)).group_by(self.defect_repository.model.status)
        )
        return {row[0] or "Unknown": int(row[1]) for row in result}

    async def by_priority(self) -> dict[str, int]:
        result = await self.defect_repository.session.execute(
            select(self.defect_repository.model.priority, func.count(self.defect_repository.model.id)).group_by(self.defect_repository.model.priority)
        )
        return {row[0] or "Unknown": int(row[1]) for row in result}

    async def by_assignment_group(self) -> dict[str, int]:
        result = await self.defect_repository.session.execute(
            select(self.defect_repository.model.assignment_group, func.count(self.defect_repository.model.id)).group_by(self.defect_repository.model.assignment_group)
        )
        return {row[0] or "Unknown": int(row[1]) for row in result}

    async def backlog_by_assignment_group(self, limit: int = 5) -> list[tuple[str, int]]:
        result = await self.defect_repository.session.execute(
            select(self.defect_repository.model.assignment_group, func.count(self.defect_repository.model.id))
            .where(self.defect_repository.model.status != "Closed")
            .group_by(self.defect_repository.model.assignment_group)
            .order_by(func.count(self.defect_repository.model.id).desc())
            .limit(limit)
        )
        return [(row[0] or "Unknown", int(row[1])) for row in result]

    async def defects_older_than(self, days: int, assignment_group: str | None = None, service_offering: str | None = None) -> list[Defect]:
        return await self.defect_repository.get_aging_defects(days_threshold=days)