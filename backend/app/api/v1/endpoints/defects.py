"""Defect CRUD endpoints for Phase 1."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.defect_repository import DefectRepository

router = APIRouter(prefix="/defects", tags=["Defects"])


class DefectCreate(BaseModel):
    number: str
    title: str
    description: str | None = None
    priority: str = "Medium"
    status: str = "Open"
    category: str = "General"
    assigned_to: str | None = None
    opened_at: datetime
    resolved_at: datetime | None = None
    sla_due: datetime | None = None
    is_sla_breached: bool = False
    reopen_count: int = 0


class DefectUpdate(BaseModel):
    number: str | None = None
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    category: str | None = None
    assigned_to: str | None = None
    opened_at: datetime | None = None
    resolved_at: datetime | None = None
    sla_due: datetime | None = None
    is_sla_breached: bool | None = None
    reopen_count: int | None = None


class DefectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    number: str
    title: str
    description: str | None = None
    priority: str
    status: str
    category: str
    assigned_to: str | None = None
    opened_at: datetime
    resolved_at: datetime | None = None
    sla_due: datetime | None = None
    is_sla_breached: bool
    reopen_count: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class PaginatedDefects(BaseModel):
    items: list[DefectOut]
    total: int
    page: int
    page_size: int
    total_pages: int


def get_repository(session: AsyncSession = Depends(get_db)) -> DefectRepository:
    return DefectRepository(session)


@router.get("", response_model=PaginatedDefects)
async def list_defects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    repository: DefectRepository = Depends(get_repository),
) -> PaginatedDefects:
    defects, total = await repository.get_all(
        {"status": status, "priority": priority, "search": search},
        page=page,
        page_size=page_size,
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedDefects(
        items=[DefectOut.model_validate(defect) for defect in defects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{defect_id}", response_model=DefectOut)
async def get_defect(defect_id: UUID, repository: DefectRepository = Depends(get_repository)) -> DefectOut:
    defect = await repository.get_by_id(defect_id)
    return DefectOut.model_validate(defect)


@router.post("", response_model=DefectOut, status_code=status.HTTP_201_CREATED)
async def create_defect(payload: DefectCreate, repository: DefectRepository = Depends(get_repository)) -> DefectOut:
    defect = await repository.create(payload.model_dump())
    return DefectOut.model_validate(defect)


@router.patch("/{defect_id}", response_model=DefectOut)
async def update_defect(
    defect_id: UUID,
    payload: DefectUpdate,
    repository: DefectRepository = Depends(get_repository),
) -> DefectOut:
    defect = await repository.update(defect_id, payload.model_dump(exclude_unset=True))
    if defect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")
    return DefectOut.model_validate(defect)


@router.delete("/{defect_id}")
async def delete_defect(defect_id: UUID, repository: DefectRepository = Depends(get_repository)) -> dict[str, str]:
    defect = await repository.get_by_id(defect_id)
    defect.is_deleted = True
    await repository.session.commit()
    return {"status": "deleted"}