from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):

    @abstractmethod
    def embed_text(self, text:str) -> list[float]:
        pass

    @abstractmethod
    def embed_documents(
        self, 
        texts: list[str]
    ) -> list[list[float]]:
        pass
    