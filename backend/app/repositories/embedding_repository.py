from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Embedding
from typing import List, Tuple


class EmbeddingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_save(self, records: List[Tuple[str, List[float]]]):
        objs = []
        for defect_id, vector in records:
            obj = Embedding(defect_id=defect_id, vector=vector)
            self.session.add(obj)
            objs.append(obj)
        await self.session.commit()
        return objs

    async def clear_all(self):
        await self.session.execute('DELETE FROM embeddings')
        await self.session.commit()

    async def get_all(self):
        res = await self.session.execute('SELECT defect_id, vector FROM embeddings')
        return res.fetchall()
