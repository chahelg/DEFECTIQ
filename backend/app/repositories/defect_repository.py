from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
import math
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Defect
from app.repositories.base_repository import BaseRepository


class DefectRepository(BaseRepository[Defect]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Defect)

    @staticmethod
    def _has_value(value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, float) and math.isnan(value):
            return False
        text = str(value).strip().lower()
        return bool(text and text not in {'nan', 'none', 'null'})

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if value in (None, ''):
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            return None

    @staticmethod
    def _normalize_priority(value: object) -> str:
        if value is None:
            return 'Medium'
        text = str(value).strip().lower()
        if text.startswith('1') or 'critical' in text:
            return 'Critical'
        if text.startswith('2') or 'high' in text:
            return 'High'
        if text.startswith('3') or 'moderate' in text or 'medium' in text:
            return 'Medium'
        if text.startswith('4') or 'low' in text:
            return 'Low'
        return str(value).strip().title() or 'Medium'

    @staticmethod
    def _normalize_status(value: object) -> str:
        if value is None:
            return 'Open'
        text = str(value).strip().lower()
        if 'closed' in text or 'cancelled' in text or 'complete' in text:
            return 'Closed'
        if text in {'resolved', 'done'}:
            return 'Resolved'
        if text in {'in progress', 'working', 'pending', 'active'}:
            return 'In Progress'
        if text in {'reopened', 're-opened'}:
            return 'Reopened'
        if text == 'on hold':
            return 'On Hold'
        return str(value).strip().title() or 'Open'

    @classmethod
    def _normalize_row(cls, row: Mapping[str, Any], fallback_number: str) -> dict[str, Any]:
        number = str(row.get('number') or row.get('defect_id') or row.get('sys_id') or fallback_number).strip()
        title = str(row.get('title') or row.get('short_description') or row.get('summary') or 'Untitled defect').strip()
        description = row.get('description') or row.get('work_notes') or row.get('close_notes')
        category = row.get('category') or row.get('service_offering') or row.get('business_mapping') or 'General'
        assigned_to = row.get('assigned_to') or row.get('assignment_group')
        opened_at = cls._parse_datetime(row.get('opened_at') or row.get('opened') or row.get('created_at')) or datetime.now(UTC)
        resolved_at = cls._parse_datetime(row.get('resolved_at') or row.get('closed_at') or row.get('closed'))
        sla_due = cls._parse_datetime(row.get('sla_due') or row.get('sla_due_date'))
        priority = cls._normalize_priority(row.get('priority'))
        status = cls._normalize_status(row.get('status') or row.get('state'))
        breached = bool(row.get('is_sla_breached') or (sla_due and resolved_at and resolved_at > sla_due))

        return {
            'number': number,
            'title': title,
            'description': None if description in (None, '') else str(description).strip(),
            'priority': priority,
            'status': status,
            'category': str(category).strip() or 'General',
            'assigned_to': None if assigned_to in (None, '') else str(assigned_to).strip(),
            'opened_at': opened_at,
            'resolved_at': resolved_at,
            'sla_due': sla_due,
            'is_sla_breached': breached,
            'reopen_count': int(row.get('reopen_count') or 0),
            'is_deleted': False,
        }

    async def bulk_upsert(self, rows: list[Mapping[str, Any]], replace_existing: bool = False) -> list[Defect]:
        if replace_existing:
            await self.session.execute(Defect.__table__.delete())
            if not rows:
                await self.session.commit()
                return []

        meaningful_rows = [
            row
            for row in rows
            if any(self._has_value(value) for value in row.values())
        ]
        if not meaningful_rows:
            await self.session.commit()
            return []

        normalized_rows = [self._normalize_row(row, fallback_number=f'ROW-{index + 1}') for index, row in enumerate(meaningful_rows)]
        numbers = [row['number'] for row in normalized_rows if row.get('number')]

        if replace_existing:
            existing: dict[str, Defect] = {}
        else:
            existing_result = await self.session.execute(select(Defect).where(Defect.number.in_(numbers)))
            existing = {defect.number: defect for defect in existing_result.scalars().all()}

        upserted: list[Defect] = []
        for row in normalized_rows:
            defect = existing.get(row['number'])
            if defect is None:
                defect = Defect(**row)
                self.session.add(defect)
            else:
                for key, value in row.items():
                    if hasattr(defect, key):
                        setattr(defect, key, value)
            upserted.append(defect)

        await self.session.commit()
        return upserted

    def _build_filters(self, filters: Mapping[str, Any] | None) -> list[Any]:
        conditions: list[Any] = [Defect.is_deleted.is_(False)]
        if not filters:
            return conditions

        status_value = filters.get("status")
        if status_value:
            conditions.append(Defect.status == status_value)

        priority_value = filters.get("priority")
        if priority_value:
            conditions.append(Defect.priority == priority_value)

        search_value = filters.get("search") or filters.get("search_text")
        if search_value:
            pattern = f"%{search_value}%"
            conditions.append(
                or_(
                    Defect.number.ilike(pattern),
                    Defect.title.ilike(pattern),
                    Defect.description.ilike(pattern),
                    Defect.category.ilike(pattern),
                    Defect.assigned_to.ilike(pattern),
                )
            )

        return conditions

    async def get_all(self, filters: Mapping[str, Any] | None = None, page: int = 1, page_size: int = 20) -> tuple[list[Defect], int]:
        conditions = self._build_filters(filters)

        count_statement = select(func.count()).select_from(Defect).where(and_(*conditions))
        count_result = await self.session.execute(count_statement)
        total = int(count_result.scalar() or 0)

        statement = (
            select(Defect)
            .where(and_(*conditions))
            .order_by(desc(Defect.opened_at))
            .offset(max(page - 1, 0) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all()), total

    async def get_by_id(self, defect_id: str) -> Defect:
        result = await self.session.execute(select(Defect).where(Defect.id == defect_id, Defect.is_deleted.is_(False)))
        defect = result.scalar_one_or_none()
        if defect is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")
        return defect

    async def get_kpis(self) -> dict[str, Any]:
        active = Defect.is_deleted.is_(False)
        total_stmt = select(func.count()).select_from(Defect).where(active)
        open_stmt = select(func.count()).select_from(Defect).where(active, Defect.status.notin_(["Closed", "Resolved"]))
        closed_stmt = select(func.count()).select_from(Defect).where(active, Defect.status.in_(["Closed", "Resolved"]))
        breached_stmt = select(func.count()).select_from(Defect).where(active, Defect.is_sla_breached.is_(True))
        critical_stmt = select(func.count()).select_from(Defect).where(active, Defect.priority == "Critical")
        reopen_rate_stmt = select(func.coalesce(func.avg(case((Defect.reopen_count > 0, 1.0), else_=0.0)) * 100.0, 0.0)).where(active)
        resolution_stmt = select(Defect.opened_at, Defect.resolved_at).where(
            active,
            Defect.resolved_at.is_not(None),
            Defect.opened_at.is_not(None),
        )

        total = int((await self.session.execute(total_stmt)).scalar() or 0)
        open_count = int((await self.session.execute(open_stmt)).scalar() or 0)
        closed_count = int((await self.session.execute(closed_stmt)).scalar() or 0)
        breached_count = int((await self.session.execute(breached_stmt)).scalar() or 0)
        critical_count = int((await self.session.execute(critical_stmt)).scalar() or 0)
        reopen_rate = float((await self.session.execute(reopen_rate_stmt)).scalar() or 0)
        resolution_rows = (await self.session.execute(resolution_stmt)).all()
        resolution_hours: list[float] = []
        for opened_at, resolved_at in resolution_rows:
            if opened_at is None or resolved_at is None:
                continue
            hours = (resolved_at - opened_at).total_seconds() / 3600.0
            resolution_hours.append(max(hours, 0.0))

        avg_resolution_hours = sum(resolution_hours) / len(resolution_hours) if resolution_hours else 0.0

        sla_compliance_pct = round(100 - ((breached_count / total) * 100), 2) if total else 100.0
        return {
            "total_defects": total,
            "open_defects": open_count,
            "closed_defects": closed_count,
            "sla_breached_count": breached_count,
            "avg_resolution_hours": round(avg_resolution_hours, 2),
            "critical_count": critical_count,
            "reopen_rate": round(reopen_rate, 2),
            "sla_compliance_pct": sla_compliance_pct,
        }

    async def get_trends(self, weeks: int = 12) -> list[dict[str, Any]]:
        start_date = datetime.now(UTC) - timedelta(weeks=weeks)
        statement = select(Defect.opened_at).where(Defect.is_deleted.is_(False), Defect.opened_at >= start_date)
        result = await self.session.execute(statement)

        rows: dict[datetime.date, int] = {}
        for (opened_at,) in result:
            if opened_at is None:
                continue
            week_date = opened_at.date() - timedelta(days=opened_at.date().weekday())
            rows[week_date] = rows.get(week_date, 0) + 1

        current_week = (datetime.now(UTC) - timedelta(days=datetime.now(UTC).weekday())).date()
        series: list[dict[str, Any]] = []
        for week_index in range(weeks - 1, -1, -1):
            week_date = current_week - timedelta(weeks=week_index)
            series.append({"week": week_date.isoformat(), "count": rows.get(week_date, 0)})
        return series

    async def get_by_priority(self) -> list[dict[str, Any]]:
        statement = (
            select(Defect.priority, func.count().label("count"))
            .where(Defect.is_deleted.is_(False))
            .group_by(Defect.priority)
            .order_by(Defect.priority)
        )
        result = await self.session.execute(statement)
        return [{"name": row.priority or "Unknown", "value": int(row.count)} for row in result]

    async def get_by_status(self) -> list[dict[str, Any]]:
        statement = (
            select(Defect.status, func.count().label("count"))
            .where(Defect.is_deleted.is_(False))
            .group_by(Defect.status)
            .order_by(Defect.status)
        )
        result = await self.session.execute(statement)
        return [{"name": row.status or "Unknown", "value": int(row.count)} for row in result]
