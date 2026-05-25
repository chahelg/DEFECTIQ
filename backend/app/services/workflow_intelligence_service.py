"""Workflow intelligence service for flow visibility and bottleneck intervention."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect


class WorkflowIntelligenceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_snapshot(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        open_filter = and_(
            Defect.is_deleted.is_(False),
            Defect.status.notin_(["Closed", "Resolved"]),
        )

        active_defects = (await self.session.execute(select(Defect).where(open_filter))).scalars().all()
        all_defects = (await self.session.execute(select(Defect).where(Defect.is_deleted.is_(False)))).scalars().all()

        week_start = now - timedelta(days=7)
        inflow_7d = len(
            [
                item
                for item in all_defects
                if self._to_utc(item.opened_at) and self._to_utc(item.opened_at) >= week_start
            ]
        )
        throughput_7d = len(
            [
                item
                for item in all_defects
                if self._to_utc(item.resolved_at) and self._to_utc(item.resolved_at) >= week_start
            ]
        )
        flow_efficiency = self._flow_efficiency(inflow_7d, throughput_7d)

        cycle_times = [
            max(0.0, (self._to_utc(item.resolved_at) - self._to_utc(item.opened_at)).total_seconds() / 86400.0)
            for item in all_defects
            if self._to_utc(item.opened_at) and self._to_utc(item.resolved_at)
        ]
        avg_cycle_time_days = round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0.0

        status_pipeline = self._status_pipeline(active_defects, now)
        blocked_items = len([item for item in active_defects if item.status in {"Blocked", "On Hold", "Pending"}])
        stale_items = len([item for item in active_defects if self._days_since_update(item, now) >= 3])

        return {
            "generated_at": now.isoformat(),
            "summary": {
                "active_items": len(active_defects),
                "inflow_7d": inflow_7d,
                "throughput_7d": throughput_7d,
                "flow_efficiency": flow_efficiency,
                "avg_cycle_time_days": avg_cycle_time_days,
                "blocked_items": blocked_items,
                "stale_items": stale_items,
            },
            "status_pipeline": status_pipeline,
            "stale_work_items": self._stale_work_items(active_defects, now),
            "recommended_actions": self._recommended_actions(status_pipeline, blocked_items, stale_items),
        }

    @staticmethod
    def _days_since_opened(item: Defect, now: datetime) -> int:
        opened_at = WorkflowIntelligenceService._to_utc(item.opened_at)
        if opened_at is None:
            return 0
        return max(0, (now - opened_at).days)

    @staticmethod
    def _days_since_update(item: Defect, now: datetime) -> int:
        updated_at = WorkflowIntelligenceService._to_utc(item.updated_at)
        if updated_at is None:
            return 0
        return max(0, (now - updated_at).days)

    @staticmethod
    def _to_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _flow_efficiency(inflow_7d: int, throughput_7d: int) -> float:
        if inflow_7d == 0:
            return 100.0 if throughput_7d > 0 else 0.0
        score = (throughput_7d / inflow_7d) * 100.0
        return round(max(0.0, min(120.0, score)), 2)

    def _status_pipeline(self, active_defects: list[Defect], now: datetime) -> list[dict[str, Any]]:
        status_map: dict[str, list[Defect]] = {}
        for item in active_defects:
            status = item.status or "Unknown"
            status_map.setdefault(status, []).append(item)

        rows: list[dict[str, Any]] = []
        for status, items in status_map.items():
            count = len(items)
            avg_age = round(sum(self._days_since_opened(item, now) for item in items) / max(count, 1), 2)
            stale_ratio = len([item for item in items if self._days_since_update(item, now) >= 3]) / max(count, 1)
            critical_ratio = len([item for item in items if item.priority == "Critical"]) / max(count, 1)
            bottleneck_score = round(min(100.0, (avg_age * 5.0) + (stale_ratio * 35.0) + (critical_ratio * 30.0)), 2)
            rows.append(
                {
                    "status": status,
                    "count": count,
                    "avg_age_days": avg_age,
                    "stale_ratio": round(stale_ratio * 100.0, 2),
                    "critical_ratio": round(critical_ratio * 100.0, 2),
                    "bottleneck_score": bottleneck_score,
                }
            )

        rows.sort(key=lambda row: row["bottleneck_score"], reverse=True)
        return rows

    def _stale_work_items(self, active_defects: list[Defect], now: datetime) -> list[dict[str, Any]]:
        items = [item for item in active_defects if self._days_since_update(item, now) >= 3]
        items.sort(key=lambda item: (self._days_since_update(item, now), self._days_since_opened(item, now)), reverse=True)

        output: list[dict[str, Any]] = []
        for item in items[:20]:
            age_days = self._days_since_opened(item, now)
            update_days = self._days_since_update(item, now)
            output.append(
                {
                    "defect_number": item.number,
                    "title": item.title,
                    "status": item.status,
                    "priority": item.priority,
                    "assignee": item.assigned_to or "Unassigned",
                    "age_days": age_days,
                    "days_since_update": update_days,
                    "intervention": self._intervention_text(item.status, update_days, item.assigned_to),
                }
            )
        return output

    @staticmethod
    def _intervention_text(status: str, days_since_update: int, assignee: str | None) -> str:
        if not assignee:
            return "Assign owner now and enforce same-day status checkpoint."
        if status in {"Blocked", "On Hold", "Pending"}:
            return "Escalate dependency owner and clear blocker in next standup."
        if days_since_update >= 5:
            return "Trigger manager follow-up; require resolution plan by end of day."
        return "Prompt assignee for progress update and next milestone."

    @staticmethod
    def _recommended_actions(status_pipeline: list[dict[str, Any]], blocked_items: int, stale_items: int) -> list[str]:
        actions: list[str] = []
        if status_pipeline:
            top = status_pipeline[0]
            actions.append(
                f"Run bottleneck intervention on '{top['status']}' stage (score {top['bottleneck_score']:.1f}) before next shift handoff."
            )
        if blocked_items > 0:
            actions.append("Resolve blocked and pending items through a dependency-clearing huddle within 4 hours.")
        if stale_items > 0:
            actions.append("Apply stale-item SLA: every item idle for 3+ days gets explicit owner update or reassignment.")
        if not actions:
            actions.append("Workflow is stable. Continue cadence checks every 30 minutes.")
        return actions
