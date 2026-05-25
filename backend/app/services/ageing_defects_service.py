"""Ageing defects snapshot service for stale backlog intelligence."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect


class AgeingDefectsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_snapshot(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        active_filter = and_(
            Defect.is_deleted.is_(False),
            Defect.status.notin_(["Closed", "Resolved"]),
        )

        active_defects = (await self.session.execute(select(Defect).where(active_filter))).scalars().all()

        rows: list[dict[str, Any]] = []
        for defect in active_defects:
            opened_at = self._to_utc(defect.opened_at)
            age_days = max(0, (now - opened_at).days) if opened_at else 0
            rows.append(
                {
                    "id": str(defect.id),
                    "number": defect.number,
                    "title": defect.title,
                    "priority": defect.priority,
                    "status": defect.status,
                    "assigned_to": defect.assigned_to or "Unassigned",
                    "is_sla_breached": bool(defect.is_sla_breached),
                    "age_days": age_days,
                }
            )

        rows.sort(key=lambda item: item["age_days"], reverse=True)

        buckets = {
            "0-3d": 0,
            "4-7d": 0,
            "8-14d": 0,
            "15-30d": 0,
            "30+d": 0,
        }
        for row in rows:
            age_days = row["age_days"]
            if age_days <= 3:
                buckets["0-3d"] += 1
            elif age_days <= 7:
                buckets["4-7d"] += 1
            elif age_days <= 14:
                buckets["8-14d"] += 1
            elif age_days <= 30:
                buckets["15-30d"] += 1
            else:
                buckets["30+d"] += 1

        stale_count = len([row for row in rows if row["age_days"] > 14])
        critical_stale = len([row for row in rows if row["age_days"] > 14 and row["priority"] == "Critical"])
        high_risk = len([row for row in rows if row["age_days"] > 30 or row["is_sla_breached"]])

        return {
            "generated_at": now.isoformat(),
            "summary": {
                "active_defects": len(rows),
                "stale_defects": stale_count,
                "critical_stale": critical_stale,
                "high_risk_queue": high_risk,
            },
            "aging_buckets": [{"bucket": key, "count": value} for key, value in buckets.items()],
            "oldest_active_defects": rows[:20],
        }

    @staticmethod
    def _to_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
