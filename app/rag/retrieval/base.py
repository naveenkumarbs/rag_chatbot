from abc import ABC, abstractmethod

class VectorStore(ABC):
    @abstractmethod
    def add_chunks(
        self, 
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict]
    ):
        pass

    @abstractmethod
    def search(
        self, 
        query_embedding: list[float], 
        top_k: int = 5
    ):
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id:str) -> None:
        pass
    