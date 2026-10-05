from fastapi import APIRouter, Query

from app.rag.retrieval.retrieval_service import (
    RetrievalService
)

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@router.get("")
def search(
    query: str = Query(
        ...,
        min_length=2 
    ),
    top_k: int = Query(
        default=5,
        ge=1,
        le=20
    )
):
    service = RetrievalService()

    results = service.search(
        query=query,
        top_k=top_k
    )

    return {
        "query": query,
        "results": results
    }