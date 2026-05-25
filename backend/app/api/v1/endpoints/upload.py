"""File upload endpoint for defect ingest."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from difflib import get_close_matches
from io import BytesIO
import re

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Defect

router = APIRouter(prefix="/upload", tags=["Upload"])

CANONICAL_COLUMNS: dict[str, list[str]] = {
    "number": ["number", "incident number", "ticket", "ticket number", "defect number", "id"],
    "title": ["short description", "title", "summary", "subject"],
    "description": ["description", "details", "long description"],
    "priority": ["priority", "severity"],
    "status": ["status", "state"],
    "category": ["category", "type", "service category", "issue type"],
    "assigned_to": ["assigned to", "assignee", "owner"],
    "opened_at": ["opened", "opened at", "created", "created at", "reported at"],
    "resolved_at": ["resolved", "resolved at", "closed", "closed at"],
    "sla_due": ["sla due", "due date", "target date", "breach date"],
}


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _read_dataframe(file_name: str, content: bytes) -> pd.DataFrame:
    if file_name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(content))
    if file_name.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .xlsx and .csv files are supported")


def _build_column_mapping(columns: Iterable[str]) -> dict[str, str]:
    available = list(columns)
    normalized_lookup = {_normalize(column): column for column in available}
    mapping: dict[str, str] = {}

    for canonical, aliases in CANONICAL_COLUMNS.items():
        candidates = [canonical, *aliases]
        found = None
        for candidate in candidates:
            normalized = _normalize(candidate)
            if normalized in normalized_lookup:
                found = normalized_lookup[normalized]
                break
        if found is None:
            close_matches = get_close_matches(candidates[0], available, n=1, cutoff=0.72)
            if close_matches:
                found = close_matches[0]
        if found is not None:
            mapping[found] = canonical
    return mapping


def _parse_datetime(value: object) -> datetime | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime() if isinstance(parsed, pd.Timestamp) else None


def _normalize_priority(value: object) -> str:
    if value is None or value == "" or pd.isna(value):
        return "Medium"
    text = str(value).strip().lower()
    if text in {"1", "critical"}:
        return "Critical"
    if text in {"2", "high"}:
        return "High"
    if text in {"3", "medium"}:
        return "Medium"
    if text in {"4", "low"}:
        return "Low"
    return str(value).strip().title()


def _normalize_status(value: object) -> str:
    if value is None or value == "" or pd.isna(value):
        return "Open"
    text = str(value).strip().lower()
    if text in {"closed", "resolved", "done", "complete"}:
        return "Closed"
    if text in {"open", "new", "pending", "in progress", "working"}:
        return str(value).strip().title() if text != "open" else "Open"
    return str(value).strip().title()


@router.post("")
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_db)) -> dict:
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload a .xlsx or .csv file")

    dataframe = _read_dataframe(file.filename, await file.read())
    mapping = _build_column_mapping(dataframe.columns)

    candidate_rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    seen_numbers: set[str] = set()

    for index, row in dataframe.iterrows():
        try:
            row_data = {target: row[source] for source, target in mapping.items() if source in row.index}
            number = str(row_data.get("number") or row.get("Number") or row.get("number") or f"ROW-{index + 1}").strip()
            if number in seen_numbers:
                errors.append({"row": index + 2, "error": f"Duplicate defect number {number}"})
                continue
            seen_numbers.add(number)

            title = str(row_data.get("title") or row.get("Short description") or row.get("title") or "Untitled defect").strip()
            description = row_data.get("description") or row.get("Description") or row.get("description")
            category = str(row_data.get("category") or row.get("Category") or "General").strip() or "General"
            assigned_to = row_data.get("assigned_to") or row.get("Assigned to") or row.get("Assigned To")
            opened_at = _parse_datetime(row_data.get("opened_at") or row.get("Opened") or row.get("opened_at")) or datetime.now(timezone.utc)
            resolved_at = _parse_datetime(row_data.get("resolved_at") or row.get("Resolved") or row.get("resolved_at"))
            sla_due = _parse_datetime(row_data.get("sla_due") or row.get("SLA due") or row.get("sla_due"))
            priority = _normalize_priority(row_data.get("priority") or row.get("Priority"))
            status_value = _normalize_status(row_data.get("status") or row.get("Status"))
            breached = bool(row_data.get("is_sla_breached") or (sla_due and resolved_at and resolved_at > sla_due))

            candidate_rows.append(
                {
                    "number": number,
                    "title": title,
                    "description": None if pd.isna(description) else description,
                    "priority": priority,
                    "status": status_value,
                    "category": category,
                    "assigned_to": None if pd.isna(assigned_to) else str(assigned_to),
                    "opened_at": opened_at,
                    "resolved_at": resolved_at,
                    "sla_due": sla_due,
                    "is_sla_breached": breached,
                    "reopen_count": int(row_data.get("reopen_count") or 0),
                    "is_deleted": False,
                }
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"row": index + 2, "error": str(exc)})

    if candidate_rows:
        existing_result = await session.execute(select(Defect.number).where(Defect.number.in_([row["number"] for row in candidate_rows])))
        existing_numbers = {str(row[0]) for row in existing_result}
    else:
        existing_numbers = set()

    rows_to_insert = [row for row in candidate_rows if row["number"] not in existing_numbers]
    if rows_to_insert:
        await session.execute(insert(Defect), rows_to_insert)
        await session.commit()

    return {
        "rows_inserted": len(rows_to_insert),
        "rows_failed": len(errors) + (len(candidate_rows) - len(rows_to_insert)),
        "column_mapping_used": {canonical: source for source, canonical in sorted(mapping.items())},
        "errors": errors,
    }