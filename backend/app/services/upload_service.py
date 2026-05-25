"""Upload service for Excel and CSV ingest workflows."""

from __future__ import annotations

from io import BytesIO

import pandas as pd
from fastapi import HTTPException, UploadFile, status

from app.repositories.upload_repository import UploadRepository
from app.schemas import UploadCompleteResponse, UploadPreviewResponse, UploadProgressResponse


class UploadService:
    def __init__(self, upload_repository: UploadRepository) -> None:
        self.upload_repository = upload_repository

    async def preview(self, file: UploadFile) -> UploadPreviewResponse:
        dataframe = self._read_file(file.filename or "upload", await file.read())
        preview_rows = dataframe.head(5).fillna("").to_dict(orient="records")
        return UploadPreviewResponse(columns=list(dataframe.columns), preview_rows=preview_rows, total_rows=len(dataframe))

    async def create_session(self, file_name: str, file_type: str, total_records: int) -> UploadProgressResponse:
        session = await self.upload_repository.create(
            {
                "file_name": file_name,
                "file_type": file_type,
                "total_records": total_records,
                "processed_records": 0,
                "failed_records": 0,
                "status": "pending",
            }
        )
        return UploadProgressResponse(
            upload_id=session.id,
            file_name=session.file_name,
            total_records=session.total_records or total_records,
            processed_records=session.processed_records,
            progress_percentage=0,
            status=session.status,
            errors=None,
        )

    async def complete(self, upload_id: str, successful_records: int, failed_records: int, warnings: list[str]) -> UploadCompleteResponse:
        session = await self.upload_repository.update(
            upload_id,
            {
                "processed_records": successful_records + failed_records,
                "failed_records": failed_records,
                "status": "completed" if failed_records == 0 else "completed_with_errors",
            },
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload session not found")
        total = session.total_records or (successful_records + failed_records)
        return UploadCompleteResponse(
            upload_id=session.id,
            file_name=session.file_name,
            total_records=total,
            successful_records=successful_records,
            failed_records=failed_records,
            warnings=warnings,
            message="Upload processed successfully",
        )

    def _read_file(self, file_name: str, file_content: bytes) -> pd.DataFrame:
        extension = file_name.lower().rsplit(".", 1)[-1]
        if extension in {"xlsx", "xls"}:
            return pd.read_excel(BytesIO(file_content))
        if extension == "csv":
            return pd.read_csv(BytesIO(file_content))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")