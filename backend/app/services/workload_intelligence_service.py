"""Workload intelligence service for balancing assignments and preventing bottlenecks."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect


class WorkloadIntelligenceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_snapshot(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        open_filter = and_(Defect.is_deleted.is_(False), Defect.status.notin_(["Closed", "Resolved"]))

        rows = await self._assignee_rows(open_filter)
        totals = self._totals(rows)
        overloaded, underutilized = self._split_load(rows)

        return {
            "generated_at": now.isoformat(),
            "summary": {
                "active_assignees": len(rows),
                "open_defects": totals["open_defects"],
                "overloaded_assignees": len(overloaded),
                "underutilized_assignees": len(underutilized),
                "workload_imbalance_score": self._imbalance_score(rows),
                "assignment_efficiency": self._assignment_efficiency(rows),
            },
            "assignee_workload": rows,
            "reassignment_candidates": self._reassignment_candidates(overloaded, underutilized),
            "recommended_actions": self._recommended_actions(overloaded, underutilized),
        }

    async def _assignee_rows(self, open_filter: Any) -> list[dict[str, Any]]:
        statement = (
            select(
                func.coalesce(Defect.assigned_to, "Unassigned").label("assignee"),
                func.count().label("open_count"),
                func.sum(case((Defect.priority == "Critical", 1), else_=0)).label("critical_count"),
                func.sum(case((Defect.priority == "High", 1), else_=0)).label("high_count"),
                func.sum(case((Defect.is_sla_breached.is_(True), 1), else_=0)).label("breached_count"),
                func.sum(case((Defect.reopen_count > 0, 1), else_=0)).label("reopen_count"),
            )
            .where(open_filter)
            .group_by(func.coalesce(Defect.assigned_to, "Unassigned"))
            .order_by(func.count().desc())
            .limit(25)
        )
        result = await self.session.execute(statement)

        rows: list[dict[str, Any]] = []
        for row in result:
            open_count = int(row.open_count or 0)
            critical_count = int(row.critical_count or 0)
            high_count = int(row.high_count or 0)
            breached_count = int(row.breached_count or 0)
            reopen_count = int(row.reopen_count or 0)

            weighted_load = open_count + (critical_count * 2.0) + (high_count * 1.4) + (breached_count * 1.6)
            capacity_index = round(max(0.0, 100.0 - weighted_load * 4.5), 2)
            workload_score = round(min(100.0, weighted_load * 5.2), 2)

            rows.append(
                {
                    "assignee": row.assignee,
                    "open_count": open_count,
                    "critical_count": critical_count,
                    "high_count": high_count,
                    "breached_count": breached_count,
                    "reopen_count": reopen_count,
                    "workload_score": workload_score,
                    "capacity_index": capacity_index,
                    "load_band": self._band(workload_score),
                }
            )
        return rows

    @staticmethod
    def _band(score: float) -> str:
        if score >= 75:
            return "overloaded"
        if score <= 35:
            return "underutilized"
        return "balanced"

    @staticmethod
    def _totals(rows: list[dict[str, Any]]) -> dict[str, int]:
        return {
            "open_defects": sum(row["open_count"] for row in rows),
            "critical": sum(row["critical_count"] for row in rows),
            "breached": sum(row["breached_count"] for row in rows),
        }

    @staticmethod
    def _split_load(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        overloaded = [row for row in rows if row["load_band"] == "overloaded"]
        underutilized = [row for row in rows if row["load_band"] == "underutilized"]
        return overloaded, underutilized

    @staticmethod
    def _imbalance_score(rows: list[dict[str, Any]]) -> float:
        if len(rows) < 2:
            return 0.0
        scores = [row["workload_score"] for row in rows]
        top = max(scores)
        bottom = min(scores)
        if top == 0:
            return 0.0
        return round(((top - bottom) / top) * 100.0, 2)

    @staticmethod
    def _assignment_efficiency(rows: list[dict[str, Any]]) -> float:
        if not rows:
            return 100.0
        overloaded_ratio = len([row for row in rows if row["load_band"] == "overloaded"]) / len(rows)
        reopen_pressure = sum(row["reopen_count"] for row in rows) / max(sum(row["open_count"] for row in rows), 1)
        efficiency = 100.0 - (overloaded_ratio * 45.0) - (reopen_pressure * 25.0)
        return round(max(0.0, min(100.0, efficiency)), 2)

    @staticmethod
    def _reassignment_candidates(overloaded: list[dict[str, Any]], underutilized: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not overloaded or not underutilized:
            return []

        candidates: list[dict[str, Any]] = []
        targets = sorted(underutilized, key=lambda row: row["workload_score"])

        for source in sorted(overloaded, key=lambda row: row["workload_score"], reverse=True)[:8]:
            target = targets[0]
            suggested_moves = max(1, int((source["workload_score"] - target["workload_score"]) // 15))
            candidates.append(
                {
                    "from_assignee": source["assignee"],
                    "to_assignee": target["assignee"],
                    "suggested_defect_moves": suggested_moves,
                    "reason": "Reduce SLA and critical defect concentration by rebalancing active queue.",
                }
            )
            targets.append(targets.pop(0))

        return candidates

    @staticmethod
    def _recommended_actions(overloaded: list[dict[str, Any]], underutilized: list[dict[str, Any]]) -> list[str]:
        actions: list[str] = []
        if overloaded:
            actions.append("Trigger workload rebalance for overloaded consultants before next SLA checkpoint.")
            actions.append("Shift at least one high-priority ticket from each overloaded assignee to the lowest-load pool.")
        if underutilized:
            actions.append("Assign new incoming high-risk defects to underutilized consultants with available capacity.")
        if not actions:
            actions.append("Workload distribution is stable; continue monitoring load bands every 30 minutes.")
        return actions
