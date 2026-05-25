"""Natural language query parsing for Ask Your Defects."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class ChatIntent:
    name: str
    confidence: float
    days: int | None = None
    assignment_group: str | None = None
    service_offering: str | None = None
    priority: str | None = None
    status: str | None = None
    raw_query: str = ""
    entities: dict[str, str] = field(default_factory=dict)


class QueryParser:
    INTENT_PATTERNS: dict[str, tuple[str, ...]] = {
        "backlog": ("backlog", "open defects", "unresolved", "pending", "aging"),
        "sla_risk": ("sla", "breach", "high-risk", "high risk", "at risk"),
        "trend": ("trend", "increasing", "decreasing", "why are", "what changed"),
        "semantic_search": ("similar", "search", "find defects", "related defects", "semantic"),
        "kpi": ("kpi", "count", "how many", "which assignment group", "top group"),
        "management_insight": ("management", "executive", "insight", "summary", "recommendation"),
    }

    def parse(self, query: str) -> ChatIntent:
        lowered = query.lower().strip()
        scored = []
        for name, keywords in self.INTENT_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score:
                scored.append((name, score))

        intent_name = scored[0][0] if scored else "general"
        confidence = min(0.55 + (scored[0][1] * 0.12 if scored else 0.0), 0.97)
        days_match = re.search(r"(\d+)\s+days?", lowered)
        days = int(days_match.group(1)) if days_match else None

        assignment_group = self._capture_phrase(query, ["assignment group", "group", "team", "queue"])
        service_offering = self._capture_phrase(query, ["service offering", "service", "product"])
        priority = self._capture_token(lowered, ["critical", "high", "medium", "low"])
        status = self._capture_token(lowered, ["open", "resolved", "closed", "reopened", "in progress", "on hold"])

        return ChatIntent(
            name=intent_name,
            confidence=confidence,
            days=days,
            assignment_group=assignment_group,
            service_offering=service_offering,
            priority=priority.title() if priority else None,
            status=status.title() if status else None,
            raw_query=query,
            entities={k: v for k, v in {
                "assignment_group": assignment_group,
                "service_offering": service_offering,
                "priority": priority,
                "status": status,
            }.items() if v},
        )

    def _capture_phrase(self, query: str, hints: list[str]) -> str | None:
        lowered = query.lower()
        for hint in hints:
            pattern = rf"{hint}\s+([a-zA-Z0-9&/\- ]{{2,}})"
            match = re.search(pattern, lowered)
            if match:
                value = match.group(1).strip(" ?.,")
                if value:
                    return value.title()
        return None

    def _capture_token(self, lowered_query: str, candidates: list[str]) -> str | None:
        for candidate in candidates:
            if candidate in lowered_query:
                return candidate
        return None
