"""Root cause analysis intelligence service for operational interventions."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect


class RootCauseAnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_snapshot(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        open_filter = and_(Defect.is_deleted.is_(False), Defect.status.notin_(["Closed", "Resolved"]))

        open_defects = (await self.session.execute(select(Defect).where(open_filter))).scalars().all()
        all_active = (await self.session.execute(select(Defect).where(Defect.is_deleted.is_(False)))).scalars().all()

        cluster_signals = self._cluster_signals(open_defects, now)
        top_recurring_patterns = self._top_patterns(all_active)
        at_risk = len([item for item in open_defects if item.is_sla_breached or item.priority in {"Critical", "High"}])

        return {
            "generated_at": now.isoformat(),
            "summary": {
                "analyzed_open_defects": len(open_defects),
                "detected_clusters": len(cluster_signals),
                "at_risk_defects": at_risk,
                "rca_confidence": self._rca_confidence(len(open_defects), cluster_signals),
                "repeat_issue_rate": self._repeat_issue_rate(all_active),
            },
            "cluster_signals": cluster_signals,
            "top_recurring_patterns": top_recurring_patterns,
            "recommended_actions": self._recommended_actions(cluster_signals, top_recurring_patterns),
        }

    def _cluster_signals(self, defects: list[Defect], now: datetime) -> list[dict[str, Any]]:
        grouped: dict[str, list[Defect]] = {}
        for defect in defects:
            key = defect.category or "Uncategorized"
            grouped.setdefault(key, []).append(defect)

        rows: list[dict[str, Any]] = []
        for category, items in grouped.items():
            total = len(items)
            breached = len([item for item in items if item.is_sla_breached])
            critical = len([item for item in items if item.priority == "Critical"])
            reopened = len([item for item in items if (item.reopen_count or 0) > 0])

            avg_age = 0.0
            if total:
                avg_age = round(
                    sum(max(0, (now - self._to_utc(item.opened_at)).days) for item in items if self._to_utc(item.opened_at)) / max(total, 1),
                    2,
                )

            signal_score = min(100.0, round((critical * 18) + (breached * 16) + (reopened * 10) + (avg_age * 2.4), 2))

            rows.append(
                {
                    "cluster": category,
                    "open_count": total,
                    "critical_count": critical,
                    "breached_count": breached,
                    "reopened_count": reopened,
                    "avg_age_days": avg_age,
                    "signal_score": signal_score,
                    "likely_cause": self._cause_label(category, items),
                }
            )

        rows.sort(key=lambda row: row["signal_score"], reverse=True)
        return rows[:12]

    def _top_patterns(self, defects: list[Defect]) -> list[dict[str, Any]]:
        keyword_counter: Counter[str] = Counter()
        for defect in defects:
            text = f"{defect.title or ''} {defect.description or ''}".lower()
            tags = self._extract_tags(text)
            keyword_counter.update(tags)

        patterns: list[dict[str, Any]] = []
        for label, count in keyword_counter.most_common(8):
            patterns.append(
                {
                    "pattern": label,
                    "occurrences": count,
                    "impact": self._impact_band(count),
                }
            )
        return patterns

    @staticmethod
    def _extract_tags(text: str) -> list[str]:
        tag_rules: dict[str, tuple[str, ...]] = {
            "Data quality regression": ("invalid", "null", "schema", "mapping", "format", "parse"),
            "Integration/API instability": ("api", "endpoint", "timeout", "gateway", "integration", "service unavailable"),
            "Authentication/authorization fault": ("auth", "token", "permission", "forbidden", "unauthorized", "credential"),
            "Deployment/configuration drift": ("deployment", "config", "environment", "version", "rollback", "release"),
            "Performance bottleneck": ("slow", "latency", "performance", "memory", "cpu", "throughput"),
            "Workflow dependency blockage": ("blocked", "dependency", "waiting", "pending", "handoff", "approval"),
        }

        matched: list[str] = []
        for label, terms in tag_rules.items():
            if any(term in text for term in terms):
                matched.append(label)

        return matched or ["Unspecified recurring defect pattern"]

    @staticmethod
    def _impact_band(occurrences: int) -> str:
        if occurrences >= 20:
            return "critical"
        if occurrences >= 10:
            return "high"
        if occurrences >= 5:
            return "medium"
        return "low"

    @staticmethod
    def _cause_label(category: str, items: list[Defect]) -> str:
        category_lower = category.lower()
        if "integration" in category_lower:
            return "Service-to-service contract or endpoint stability issue"
        if "ui" in category_lower or "frontend" in category_lower:
            return "Client-side behavior drift or inconsistent validation"
        if "backend" in category_lower:
            return "Business rule or orchestration logic regression"
        if "data" in category_lower or "etl" in category_lower:
            return "Data pipeline quality or mapping inconsistency"
        unassigned_ratio = len([item for item in items if not item.assigned_to]) / max(len(items), 1)
        if unassigned_ratio >= 0.35:
            return "Ownership and triage gap causing unresolved queue build-up"
        return "Repeated operational handling gap in this defect cluster"

    @staticmethod
    def _repeat_issue_rate(defects: list[Defect]) -> float:
        if not defects:
            return 0.0
        repeated = len([item for item in defects if (item.reopen_count or 0) > 0])
        return round((repeated / len(defects)) * 100.0, 2)

    @staticmethod
    def _rca_confidence(open_count: int, clusters: list[dict[str, Any]]) -> float:
        if open_count == 0:
            return 0.0
        coverage = min(1.0, len(clusters) / max(open_count / 4, 1))
        severity_spread = 0.0
        if clusters:
            top_score = clusters[0]["signal_score"]
            tail_score = clusters[-1]["signal_score"]
            if top_score > 0:
                severity_spread = min(1.0, (top_score - tail_score) / top_score)
        confidence = (coverage * 65.0) + (severity_spread * 35.0)
        return round(max(35.0, min(98.0, confidence)), 2)

    @staticmethod
    def _recommended_actions(
        cluster_signals: list[dict[str, Any]],
        top_patterns: list[dict[str, Any]],
    ) -> list[str]:
        actions: list[str] = []
        if cluster_signals:
            top_cluster = cluster_signals[0]
            actions.append(
                f"Launch RCA swarm for '{top_cluster['cluster']}' cluster with score {top_cluster['signal_score']:.1f} and owner accountability matrix."
            )

        if top_patterns:
            top_pattern = top_patterns[0]
            actions.append(
                f"Create prevention control for recurring pattern '{top_pattern['pattern']}' and measure recurrence weekly."
            )

        severe_clusters = len([row for row in cluster_signals if row["signal_score"] >= 75])
        if severe_clusters >= 3:
            actions.append("Open cross-functional corrective action plan across product, engineering, and operations leads.")

        if not actions:
            actions.append("RCA signals are currently stable; continue daily trend monitoring.")

        return actions

    @staticmethod
    def _to_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
