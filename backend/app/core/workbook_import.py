"""Workbook-backed defect import helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.defect_repository import DefectRepository
from app.services.ingest_service import parse_file


async def import_defects_from_workbook(session: AsyncSession, workbook_path: Path, replace_existing: bool = True) -> dict[str, Any]:
    if not workbook_path.exists():
        return {"source": str(workbook_path), "rows_found": 0, "rows_imported": 0, "status": "missing"}

    records = parse_file(str(workbook_path))
    if not records:
        return {"source": str(workbook_path), "rows_found": 0, "rows_imported": 0, "status": "empty"}

    repository = DefectRepository(session)
    imported = await repository.bulk_upsert(records, replace_existing=replace_existing)
    return {"source": str(workbook_path), "rows_found": len(records), "rows_imported": len(imported), "status": "imported"}