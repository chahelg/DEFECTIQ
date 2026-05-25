"""SLA risk intelligence service for operational interventions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect


class SLARiskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_risk_snapshot(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        open_filter = and_(
            Defect.is_deleted.is_(False),
            Defect.status.notin_(["Closed", "Resolved"]),
        )

        open_defects = (await self.session.execute(select(Defect).where(open_filter))).scalars().all()

        risk_rows: list[dict[str, Any]] = []
        for defect in open_defects:
            opened_at = self._to_utc(defect.opened_at)
            age_days = max(0, (now - opened_at).days) if opened_at else 0
            hours_to_sla = self._hours_to_sla(defect.sla_due, now)
            breach_probability = self._breach_probability(defect.priority, age_days, defect.is_sla_breached, hours_to_sla)
            risk_level = self._risk_level(breach_probability)

            risk_rows.append(
                {
                    "defect_number": defect.number,
                    "title": defect.title,
                    "priority": defect.priority,
                    "status": defect.status,
                    "assignee": defect.assigned_to or "Unassigned",
                    "age_days": age_days,
                    "hours_to_sla": hours_to_sla,
                    "breach_probability": round(breach_probability, 2),
                    "risk_level": risk_level,
                    "recommended_intervention": self._recommended_intervention(risk_level, hours_to_sla, defect.assigned_to),
                }
            )

        risk_rows.sort(key=lambda item: item["breach_probability"], reverse=True)

        top_risk = risk_rows[:15]
        high_risk = [row for row in risk_rows if row["risk_level"] in {"high", "critical"}]

        return {
            "generated_at": now.isoformat(),
            "summary": {
                "open_defects": len(risk_rows),
                "at_risk_defects": len(high_risk),
                "critical_risk": len([row for row in risk_rows if row["risk_level"] == "critical"]),
                "avg_breach_probability": round(sum(row["breach_probability"] for row in risk_rows) / len(risk_rows), 2) if risk_rows else 0.0,
            },
            "risk_heatmap": await self._risk_heatmap(),
            "assignment_group_risk": await self._assignment_risk(open_filter),
            "top_risk_defects": top_risk,
            "actions": self._global_actions(high_risk),
        }

    async def _risk_heatmap(self) -> list[dict[str, Any]]:
        statement = (
            select(Defect.priority, Defect.status, func.count().label("count"))
            .where(Defect.is_deleted.is_(False), Defect.status.notin_(["Closed", "Resolved"]))
            .group_by(Defect.priority, Defect.status)
            .order_by(func.count().desc())
        )
        result = await self.session.execute(statement)
        return [
            {
                "priority": row.priority or "Unknown",
                "status": row.status or "Unknown",
                "count": int(row.count),
            }
            for row in result
        ]

    async def _assignment_risk(self, open_filter: Any) -> list[dict[str, Any]]:
        statement = (
            select(
                func.coalesce(Defect.assigned_to, "Unassigned").label("assignee"),
                func.count().label("open_count"),
                func.sum(case((Defect.is_sla_breached.is_(True), 1), else_=0)).label("breached_count"),
            )
            .where(open_filter)
            .group_by(func.coalesce(Defect.assigned_to, "Unassigned"))
            .order_by(func.count().desc())
            .limit(12)
        )
        result = await self.session.execute(statement)

        rows: list[dict[str, Any]] = []
        for row in result:
            open_count = int(row.open_count or 0)
            breached_count = int(row.breached_count or 0)
            risk_ratio = (breached_count / open_count) * 100 if open_count else 0.0
            rows.append(
                {
                    "assignee": row.assignee,
                    "open_count": open_count,
                    "breached_count": breached_count,
                    "risk_ratio": round(risk_ratio, 2),
                }
            )
        return rows

    @staticmethod
    def _hours_to_sla(sla_due: datetime | None, now: datetime) -> float | None:
        if sla_due is None:
            return None
        normalized_due = sla_due if sla_due.tzinfo is not None else sla_due.replace(tzinfo=UTC)
        delta = normalized_due - now
        return round(delta.total_seconds() / 3600.0, 2)

    @staticmethod
    def _to_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _breach_probability(priority: str, age_days: int, already_breached: bool, hours_to_sla: float | None) -> float:
        base = 0.25
        if priority == "Critical":
            base += 0.35
        elif priority == "High":
            base += 0.2
        elif priority == "Medium":
            base += 0.1

        base += min(0.3, age_days * 0.015)

        if already_breached:
            base += 0.25

        if hours_to_sla is not None:
            if hours_to_sla < 0:
                base += 0.25
            elif hours_to_sla <= 12:
                base += 0.2
            elif hours_to_sla <= 24:
                base += 0.1

        return min(1.0, base)

    @staticmethod
    def _risk_level(probability: float) -> str:
        if probability >= 0.8:
            return "critical"
        if probability >= 0.65:
            return "high"
        if probability >= 0.45:
            return "medium"
        return "low"

    @staticmethod
    def _recommended_intervention(risk_level: str, hours_to_sla: float | None, assignee: str | None) -> str:
        if risk_level == "critical":
            if hours_to_sla is not None and hours_to_sla < 0:
                return "Escalate immediately and assign incident commander to recovery bridge."
            return "Escalate to support lead and add secondary resolver within this shift."
        if risk_level == "high":
            if not assignee:
                return "Assign owner now and enforce 4-hour progress checkpoint."
            return "Reprioritize queue and schedule focused resolution block today."
        if risk_level == "medium":
            return "Monitor daily and prepare fallback assignment if no update in 8 hours."
        return "Continue normal handling with SLA watch enabled."

    @staticmethod
    def _global_actions(high_risk_rows: list[dict[str, Any]]) -> list[str]:
        if not high_risk_rows:
            return ["Current SLA exposure is stable. Maintain SLA watch and daily review cadence."]

        actions = [
            "Trigger high-risk triage meeting for the top 10 SLA-risk defects.",
            "Reassign unowned high-risk defects to available consultants before end of day.",
            "Apply escalation protocol to all critical-risk defects with <12h SLA window.",
        ]
        if len(high_risk_rows) >= 8:
            actions.append("Open temporary surge capacity plan for overloaded assignment groups.")
        return actions
