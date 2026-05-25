from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embedding_service import embedding_service
from app.db.session import AsyncSessionLocal

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post('/search/semantic')
async def semantic_search(req: SearchRequest, db: AsyncSession = Depends(get_db)):
    # ensure index exists
    count = 0
    if not embedding_service.load_index():
        count = await embedding_service.build_index(db)
    results = embedding_service.search(req.query, req.top_k)
    return {'results': results, 'indexed': count}
