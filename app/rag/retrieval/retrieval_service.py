import logging
import time 

from app.core.config import settings

from app.rag.embeddings.ollama_provider import (
    OllamaEmbeddingProvider
)

from app.rag.retrieval.chroma_store import (
    ChromaVectorStore
)

from app.rag.reranking.cross_encoder_reranker import (
    CrossEncoderReranker
)

from app.core.retrieval_cache import RetrievalCache
from app.core.metrics import (
    RETRIEVAL_CACHE_HITS_TOTAL,
    RETRIEVAL_CACHE_MISSES_TOTAL,
    RETRIEVAL_DURATION_SECONDS,
    RERANK_DURATION_SECONDS
)

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        self.embedding_provider = (
            OllamaEmbeddingProvider()
        )

        self.vector_store = (
            ChromaVectorStore()
        )

        self.reranker = (
            CrossEncoderReranker()
        )

    def search(
            self,
            query: str,
            top_k: int = 5
    ) -> list[dict]:

        candidate_k = max( top_k *4, 8)
        start = time.perf_counter()
        cached_candidates = RetrievalCache.get(query=query, candidate_k=candidate_k)
        items = []
        if cached_candidates is not None:
            RETRIEVAL_CACHE_HITS_TOTAL.inc()
            logger.info("Retrieval cahce HIT", extra={"query": query, "candidate_k": candidate_k})
            items = cached_candidates
        else:
            RETRIEVAL_CACHE_MISSES_TOTAL.inc()
            logger.info("Retrieval cahce MISS", extra={"query": query, "candidate_k": candidate_k})
            query_embedding = (
                self.embedding_provider.embed_text(query)
            )
            result = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=candidate_k
            )

            
            documents = result["documents"][0]
            metadatas = result["metadatas"][0]
            distances = result["distances"][0]

            for document, metadata, distance in zip(
                documents,
                metadatas,
                distances
            ):
                if distance > settings.rag_max_distance:
                    continue

                items.append(
                    {
                        "text": document,
                        "metadata": metadata,
                        "retrieval_distance": float(distance)
                    }
                )

                RetrievalCache.set(query=query, candidates=items, candidate_k=candidate_k)
        duration = (time.perf_counter() - start)
        RETRIEVAL_DURATION_SECONDS.observe(duration)

        rerank_start = time.perf_counter()
        results = self.reranker.rerank(
            query = query,
            candidates = items,
            top_k=top_k
        )

        RERANK_DURATION_SECONDS.observe(time.perf_counter() - rerank_start)

        return results 