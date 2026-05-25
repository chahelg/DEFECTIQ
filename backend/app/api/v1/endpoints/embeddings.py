"""Embedding and vector search endpoints."""

from fastapi import APIRouter, Depends

from app.schemas import BatchIndexRequest, BatchIndexResponse, VectorSearchRequest, VectorSearchResponse
from app.services.nlp_service import NLPService
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_vector_search_service() -> VectorSearchService:
    return VectorSearchService()


def get_nlp_service() -> NLPService:
    return NLPService()


@router.post("/encode")
async def encode_texts(texts: list[str], service: EmbeddingService = Depends(get_embedding_service)) -> dict[str, int | list[list[float]]]:
    service.ensure_directories()
    embeddings = service.encode(texts)
    return {"count": len(embeddings), "dimension": len(embeddings[0]) if embeddings else 0, "embeddings": embeddings}


@router.post("/search", response_model=VectorSearchResponse)
async def search_vectors(payload: VectorSearchRequest, service: VectorSearchService = Depends(get_vector_search_service)) -> VectorSearchResponse:
    return VectorSearchResponse(query=payload.query, results=service.search(payload.query, payload.top_k))


@router.post("/index", response_model=BatchIndexResponse)
async def index_documents(payload: BatchIndexRequest, service: NLPService = Depends(get_nlp_service)) -> BatchIndexResponse:
    result = await service.index_documents(payload.documents)
    return BatchIndexResponse(**result)