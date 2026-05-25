from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.ingest_service import parse_file
from app.repositories.defect_repository import DefectRepository
import tempfile

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post('/ingest/upload')
async def upload(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not (file.filename.endswith('.csv') or file.filename.lower().endswith(('.xls', '.xlsx'))):
        raise HTTPException(status_code=400, detail='Unsupported file type')
    with tempfile.NamedTemporaryFile(delete=False, suffix='_' + file.filename) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp.flush()
        path = tmp.name

    records = parse_file(path)
    repo = DefectRepository(db)
    inserted = await repo.bulk_upsert(records)
    return {'imported': len(inserted)}
