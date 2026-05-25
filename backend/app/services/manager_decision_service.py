"""Operational decision services for manager command workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect


class ManagerDecisionService:
    """Aggregates operational intelligence for management decisions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_command_center_snapshot(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        active_filter = Defect.is_deleted.is_(False)
        open_filter = and_(active_filter, Defect.status.notin_(["Closed", "Resolved"]))

        total = int((await self.session.execute(select(func.count()).select_from(Defect).where(active_filter))).scalar() or 0)
        open_count = int((await self.session.execute(select(func.count()).select_from(Defect).where(open_filter))).scalar() or 0)
        critical_open = int(
            (
                await self.session.execute(
                    select(func.count()).select_from(Defect).where(open_filter, Defect.priority == "Critical")
                )
            ).scalar()
            or 0
        )
        breached_open = int(
            (
                await self.session.execute(
                    select(func.count()).select_from(Defect).where(open_filter, Defect.is_sla_breached.is_(True))
                )
            ).scalar()
            or 0
        )

        mttr_hours = await self._mttr_hours(active_filter)
        escalation_risk_index = round(self._safe_pct(critical_open + breached_open, max(open_count, 1)), 2)
        operational_risk_index = round(min(100.0, escalation_risk_index * 0.55 + self._safe_pct(open_count, max(total, 1)) * 0.45), 2)

        team_load = await self._team_load_rows(open_filter)
        attention_items = await self._high_risk_defects(open_filter, now)

        recommendations: list[str] = []
        if breached_open > 0:
            recommendations.append("Escalate breached tickets older than 48h to support lead and assign recovery owner.")
        if critical_open > 0:
            recommendations.append("Create a critical defect swarm for unresolved P1/P0 backlog before next shift handoff.")
        overloaded = [row for row in team_load if row["workload_score"] >= 70]
        if overloaded:
            recommendations.append("Rebalance assignments from overloaded consultants to the lowest-load pool this cycle.")
        if not recommendations:
            recommendations.append("Maintain current cadence; monitor top 5 aging tickets for early intervention.")

        return {
            "generated_at": now.isoformat(),
            "executive_kpis": {
                "sla_breach_pct": round(self._safe_pct(breached_open, max(open_count, 1)), 2),
                "mttr_hours": round(mttr_hours, 2),
                "delivery_risk_score": operational_risk_index,
                "critical_backlog": critical_open,
                "service_instability_index": round(min(100.0, self._safe_pct(breached_open + critical_open, max(total, 1))), 2),
                "operational_risk_index": operational_risk_index,
            },
            "operational_kpis": {
                "open_defects": open_count,
                "breached_open_defects": breached_open,
                "workload_imbalance": self._workload_imbalance(team_load),
                "defect_inflow_velocity_7d": await self._inflow_velocity(days=7),
                "workflow_bottleneck_score": round(min(100.0, self._safe_pct(await self._aging_over_days(14), max(open_count, 1))), 2),
                "reopen_risk": round(await self._reopen_risk(active_filter), 2),
            },
            "attention_items": attention_items,
            "team_load": team_load,
            "recommended_actions": recommendations,
        }

    async def get_kpi_ontology_snapshot(self) -> dict[str, Any]:
        snapshot = await self.get_command_center_snapshot()
        exec_kpis = snapshot["executive_kpis"]
        ops_kpis = snapshot["operational_kpis"]

        ai_confidence = round(max(40.0, 100.0 - ops_kpis["workflow_bottleneck_score"] * 0.3), 2)
        duplicate_quality = round(min(95.0, 60.0 + (100.0 - ops_kpis["workload_imbalance"]) * 0.25), 2)
        rca_confidence = round(max(35.0, 100.0 - exec_kpis["delivery_risk_score"] * 0.5), 2)

        return {
            "generated_at": snapshot["generated_at"],
            "layers": {
                "executive": {
                    "sla_breach_pct": exec_kpis["sla_breach_pct"],
                    "mttr": exec_kpis["mttr_hours"],
                    "delivery_risk_score": exec_kpis["delivery_risk_score"],
                    "critical_backlog": exec_kpis["critical_backlog"],
                    "service_instability_index": exec_kpis["service_instability_index"],
                    "operational_risk_index": exec_kpis["operational_risk_index"],
                },
                "operational": {
                    "consultant_utilization": round(min(100.0, 40.0 + ops_kpis["workload_imbalance"] * 0.6), 2),
                    "workload_imbalance": ops_kpis["workload_imbalance"],
                    "assignment_efficiency": round(max(0.0, 100.0 - ops_kpis["workflow_bottleneck_score"] * 0.7), 2),
                    "defect_inflow_velocity": ops_kpis["defect_inflow_velocity_7d"],
                    "workflow_bottleneck_score": ops_kpis["workflow_bottleneck_score"],
                    "reopen_risk": ops_kpis["reopen_risk"],
                },
                "ai": {
                    "prediction_confidence": ai_confidence,
                    "duplicate_detection_quality": duplicate_quality,
                    "semantic_similarity_confidence": round((ai_confidence + duplicate_quality) / 2, 2),
                    "rca_confidence_score": rca_confidence,
                },
            },
            "formula_notes": [
                "Executive and operational scores are derived from live defect status, SLA breach flags, aging, and reopen patterns.",
                "AI layer in this phase is calibrated from operational stability signals until dedicated model quality telemetry is introduced.",
            ],
        }

    async def _team_load_rows(self, open_filter: Any) -> list[dict[str, Any]]:
        statement = (
            select(
                func.coalesce(Defect.assigned_to, "Unassigned").label("assignee"),
                func.count().label("open_count"),
                func.sum(case((Defect.priority == "Critical", 1), else_=0)).label("critical_count"),
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
            critical_count = int(row.critical_count or 0)
            breached_count = int(row.breached_count or 0)
            workload_score = min(100.0, round(open_count * 6 + critical_count * 12 + breached_count * 10, 2))
            rows.append(
                {
                    "assignee": row.assignee,
                    "open_count": open_count,
                    "critical_count": critical_count,
                    "breached_count": breached_count,
                    "workload_score": workload_score,
                }
            )
        return rows

    async def _high_risk_defects(self, open_filter: Any, now: datetime) -> list[dict[str, Any]]:
        result = await self.session.execute(
            select(Defect)
            .where(open_filter)
            .order_by(Defect.opened_at.asc())
            .limit(20)
        )
        rows = result.scalars().all()

        scored: list[dict[str, Any]] = []
        for defect in rows:
            age_days = max(0, (now - defect.opened_at).days) if defect.opened_at else 0
            score = (
                35 if defect.priority == "Critical" else 20 if defect.priority == "High" else 10
            ) + (25 if defect.is_sla_breached else 0) + min(30, age_days)
            scored.append(
                {
                    "defect_number": defect.number,
                    "title": defect.title,
                    "priority": defect.priority,
                    "status": defect.status,
                    "assignee": defect.assigned_to or "Unassigned",
                    "age_days": age_days,
                    "risk_score": min(100, score),
                }
            )

        scored.sort(key=lambda item: item["risk_score"], reverse=True)
        return scored[:8]

    async def _mttr_hours(self, active_filter: Any) -> float:
        rows = (
            await self.session.execute(
                select(Defect.opened_at, Defect.resolved_at)
                .where(active_filter, Defect.opened_at.is_not(None), Defect.resolved_at.is_not(None))
            )
        ).all()
        samples: list[float] = []
        for opened_at, resolved_at in rows:
            if opened_at is None or resolved_at is None:
                continue
            samples.append(max(0.0, (resolved_at - opened_at).total_seconds() / 3600.0))
        return sum(samples) / len(samples) if samples else 0.0

    async def _inflow_velocity(self, days: int) -> float:
        cutoff = datetime.now(UTC).replace(microsecond=0)
        cutoff = cutoff.fromtimestamp(cutoff.timestamp() - (days * 86400), tz=UTC)
        count = int(
            (
                await self.session.execute(
                    select(func.count()).select_from(Defect).where(Defect.is_deleted.is_(False), Defect.opened_at >= cutoff)
                )
            ).scalar()
            or 0
        )
        return round(count / max(days, 1), 2)

    async def _aging_over_days(self, days: int) -> int:
        cutoff = datetime.now(UTC).replace(microsecond=0)
        cutoff = cutoff.fromtimestamp(cutoff.timestamp() - (days * 86400), tz=UTC)
        return int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(Defect)
                    .where(
                        Defect.is_deleted.is_(False),
                        Defect.status.notin_(["Closed", "Resolved"]),
                        Defect.opened_at < cutoff,
                    )
                )
            ).scalar()
            or 0
        )

    async def _reopen_risk(self, active_filter: Any) -> float:
        value = (
            await self.session.execute(
                select(func.coalesce(func.avg(case((Defect.reopen_count > 0, 1.0), else_=0.0)) * 100.0, 0.0)).where(active_filter)
            )
        ).scalar()
        return float(value or 0.0)

    @staticmethod
    def _safe_pct(value: float | int, total: float | int) -> float:
        if not total:
            return 0.0
        return float(value) / float(total) * 100.0

    @staticmethod
    def _workload_imbalance(team_rows: list[dict[str, Any]]) -> float:
        if len(team_rows) < 2:
            return 0.0
        scores = [row["workload_score"] for row in team_rows]
        max_score = max(scores)
        min_score = min(scores)
        if max_score == 0:
            return 0.0
        return round(((max_score - min_score) / max_score) * 100.0, 2)
