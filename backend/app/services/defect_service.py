"""Defect business logic service."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.defect_repository import DefectRepository
from app.schemas import DefectCreate, DefectFilterRequest, DefectResponse, DefectUpdate, PaginatedResponse, PaginationMeta


class DefectService:
    def __init__(self, defect_repository: DefectRepository):
        self.defect_repository = defect_repository

    async def create_defect(self, payload: DefectCreate) -> DefectResponse:
        existing = await self.defect_repository.get_by_ticket_id(payload.ticket_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket already exists")
        defect = await self.defect_repository.create(payload.model_dump())
        return DefectResponse.model_validate(defect)

    async def get_defect(self, defect_id: str) -> DefectResponse:
        defect = await self.defect_repository.get_by_id(defect_id)
        if defect is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")
        return DefectResponse.model_validate(defect)

    async def update_defect(self, defect_id: str, payload: DefectUpdate) -> DefectResponse:
        defect = await self.defect_repository.update(defect_id, payload.model_dump(exclude_unset=True))
        if defect is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")
        return DefectResponse.model_validate(defect)

    async def delete_defect(self, defect_id: str) -> None:
        deleted = await self.defect_repository.delete(defect_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")

    async def list_defects(self, filters: DefectFilterRequest | None = None) -> PaginatedResponse:
        request_filters = filters or DefectFilterRequest()
        defects, total = await self.defect_repository.search(request_filters)
        total_pages = max(1, (total + request_filters.page_size - 1) // request_filters.page_size)
        return PaginatedResponse(
            items=[DefectResponse.model_validate(defect) for defect in defects],
            meta=PaginationMeta(
                page=request_filters.page,
                page_size=request_filters.page_size,
                total=total,
                total_pages=total_pages,
            ),
        )