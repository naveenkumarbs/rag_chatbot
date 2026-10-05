import httpx
import logging 

from app.core.config import settings
from app.rag.embeddings.base import EmbeddingProvider
from app.core.cache import EmbeddingCache

from app.core.metrics import (
    EMBEDDING_CACHE_HITS_TOTAL,
    EMBEDDING_CACHE_MISSES_TOTAL
)

logger = logging.getLogger(__name__)

class OllamaEmbeddingProvider(EmbeddingProvider):

    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_embedding_model

    def embed_text(self, text: str) -> list[float]:
        cached_embedding = (EmbeddingCache.get(model=self.model, text=text))
        if cached_embedding is not None:
            logger.info("Retrieval cahce HIT", extra={"model": self.model})
            EMBEDDING_CACHE_HITS_TOTAL.inc()
            return cached_embedding
        logger.info("Retrieval cahce MISS", extra={"model": self.model})
        EMBEDDING_CACHE_MISSES_TOTAL.inc() 
        embeddings = self.embed_documents([text])
        if not embeddings:
            raise RuntimeError(
                "Ollama returned no embedding for the supplied text."
            )
        embedding = embeddings[0]
        EmbeddingCache.set(model=self.model, text=text, embedding=embedding)
        return embeddings[0] 

    def embed_documents(
            self,
            texts: list[str]
    ) -> list[list[float]]:
        if not texts:
            return []

        # batch_size = 10

        all_embeddings = []
        for index, text in enumerate(texts):
        #for start in range(0,len(texts), batch_size):
            # batch = texts[start:start+batch_size]
        
            response = httpx.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.model,
                    "input": text
                }, 
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=600.0,
                    write=60.0,
                    pool=10.0
                )
            )

            response.raise_for_status()

            data = response.json()

            '''
            batch_embeddings = data.get("embeddings", [])
            if not batch_embeddings:
                raise RuntimeError(
                    "Ollama returned no embeddings "
                    f"for batch starting at index {start}. "
                    f"Raw response: {data}"
                )

            if len(batch_embeddings)!=len(batch):
                raise RuntimeError(
                    "Embeddings count mismatch: "
                    f"batch_inputs={len(batch)}, "
                    f"batch_embeddings={len(batch_embeddings)}"
                )

            all_embeddings.extend(batch_embeddings)
            '''
            embeddings = data.get("embeddings", [])
            if not embeddings:
                raise RuntimeError(
                    "Ollama returned no embedding "
                    f"for chunk {index}. "
                    f"Raw response: {data}"
                )
            embedding = embeddings[0]

            all_embeddings.append(embedding)

            print (
                f"Embedded chunk "
                f"{index+1}/{len(texts)}"
            )
            logger.info("Embedded chunk ", extra={"index": index+1, "length": len(texts)})

        if len(all_embeddings) != len(texts):
            raise RuntimeError(
                "Final embedding count mismatch: "
                f"inputs={len(texts)},"
                f"embeddings={len(all_embeddings)}"
            )
        return all_embeddings
        
        