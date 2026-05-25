"""Dashboard metrics and chart service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.repositories.defect_repository import DefectRepository
from app.schemas import DashboardResponse, KPIResponse, TrendData


class DashboardService:
    def __init__(self, defect_repository: DefectRepository):
        self.defect_repository = defect_repository

    async def get_dashboard(self) -> DashboardResponse:
        metrics = await self.defect_repository.get_kpi_metrics()
        by_service = await self.defect_repository.get_defects_by_service()
        by_assignment_group = await self._count_by_field("assignment_group")
        by_priority = await self._count_by_field("priority")

        return DashboardResponse(
            kpis=KPIResponse(
                total_defects=metrics["total_defects"],
                open_defects=metrics["open_defects"],
                closed_defects=metrics["closed_defects"],
                critical_defects=metrics["critical_defects"],
                sla_breach_percentage=metrics["sla_breach_percentage"],
            ),
            trend_data=[],
            by_priority=by_priority,
            by_assignment_group=by_assignment_group,
            by_service=by_service,
            sla_compliance={
                "breached": metrics["sla_breached_count"],
                "compliant": metrics["total_defects"] - metrics["sla_breached_count"],
            },
            aging_distribution=await self._aging_distribution(),
        )

    async def _count_by_field(self, field_name: str) -> dict[str, int]:
        statement = select(getattr(self.defect_repository.model, field_name), func.count(self.defect_repository.model.id)).group_by(getattr(self.defect_repository.model, field_name))
        result = await self.defect_repository.session.execute(statement)
        return {row[0] or "Unknown": int(row[1]) for row in result}

    async def _aging_distribution(self) -> dict[str, int]:
        buckets = {"0-7": 0, "8-30": 0, "31-60": 0, "61+": 0}
        now = datetime.now(timezone.utc)
        for defect in await self.defect_repository.get_open_defects():
            if defect.opened_at is None:
                continue
            age_days = (now - defect.opened_at).days
            if age_days <= 7:
                buckets["0-7"] += 1
            elif age_days <= 30:
                buckets["8-30"] += 1
            elif age_days <= 60:
                buckets["31-60"] += 1
            else:
                buckets["61+"] += 1
        return buckets