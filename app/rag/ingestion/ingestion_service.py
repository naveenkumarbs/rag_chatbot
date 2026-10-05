from pathlib import Path
from uuid import uuid4

from app.rag.chunking.text_chunker import TextChunker
from app.rag.embeddings.ollama_provider import (
    OllamaEmbeddingProvider
)
from app.rag.ingestion.document_loader import (
    DocumentLoader
)
from app.rag.retrieval.chroma_store import (
    ChromaVectorStore
)

class IngestionService:
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.embedding_provider = (
            OllamaEmbeddingProvider()
        )

        self.vector_store = ChromaVectorStore()

    def ingest(self, file_path: str, 
               original_filename: str | None = None, 
               document_id: str | None = None) -> dict:
        text = self.loader.load(file_path)
        chunks = self.chunker.chunk(text)

        if not chunks:
            raise ValueError(
                "No text coule be extracted from document"
            )
        embeddings = (
            self.embedding_provider.embed_documents(chunks)
        )

        if document_id is None:
            document_id = str(uuid4())

        # filename = Path(file_path).name
        stored_filename = Path(file_path).name

        display_filename = (
            original_filename
            if original_filename
            else stored_filename 
        )
        
        ids = []
        metadatas = [] 

        for index, _ in enumerate(chunks):
            ids.append(
                f"{document_id}_{index}"
            )

            metadata = {
                    "document_id": str(document_id),
                    "filename": str(display_filename),
                    "stored_filename": str(stored_filename),
                    "chunk_index": int(index)
                }
            metadatas.append(metadata)

        if not (
            len(chunks)
            == len(embeddings)
            == len(ids)
            == len(metadatas)
        ):
            raise RuntimeError(
                "Ingestion length mismatch: "
                f"chunks={len(chunks)}, "
                f"embeddings={len(embeddings)}, "
                f"ids={len(ids)}, "
                f"metadatas={len(metadatas)}"
            )

        print("Sample metadata:", metadatas[0])
        print(
            "Metadata types:",
            {
                key: type(value).__name__
                for key, value in metadatas[0].items()
            }
        )
        self.vector_store.add_chunks(
            ids=ids,
            texts=chunks,
            embeddings=embeddings,
            metadata=metadatas
        )

        return {
            "document_id": document_id,
            "filename": display_filename,
            "chunks": len(chunks)
        }