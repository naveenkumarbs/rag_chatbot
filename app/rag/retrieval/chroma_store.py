import chromadb

from app.core.config import settings as ChromaSettings
from app.rag.retrieval.base import VectorStore

class ChromaVectorStore(VectorStore):
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=ChromaSettings.chroma_db_path
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=ChromaSettings.chroma_collection
            )
        )

    def add_chunks(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict]
    ):
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings, #this is to use our own embeddings rather than using chroma's default embedding model    
            metadatas=metadata
        )

    def search(
            self,
            query_embedding: list[float],
            top_k: int = 5
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

    def delete_by_document_id(self, document_id:str) -> None:
        self.collection.delete(
            where={"document_id": str(document_id)}
        )