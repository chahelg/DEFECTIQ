from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_service import backlog_by_assignment_group, trends_by_week
from app.models.models import AnalyticsCache
from sqlalchemy import insert
from datetime import datetime


async def refresh_snapshots(db: AsyncSession):
    backlog = await backlog_by_assignment_group(db)
    trends = await trends_by_week(db)

    # upsert snapshots into analytics_cache with keys
    await db.execute("DELETE FROM analytics_cache WHERE key IN ('backlog_snapshot','trends_snapshot')")
    await db.execute(insert(AnalyticsCache).values([{'key':'backlog_snapshot','value':backlog,'created_at':datetime.utcnow()}, {'key':'trends_snapshot','value':trends,'created_at':datetime.utcnow()}]))
    await db.commit()


async def get_snapshot(db: AsyncSession, key: str):
    res = await db.execute("SELECT value FROM analytics_cache WHERE key = :k", {'k': key})
    row = res.fetchone()
    if not row:
        return None
    return row[0]
