import time
import logging 

from app.rag.generation.context_builder import ContextBuilder
from app.rag.generation.prompt_builder import PromptBuilder
from app.rag.providers.ollama_provider import OllamaLLMProvider
from app.rag.retrieval.retrieval_service import RetrievalService
from app.rag.query.query_writer import QueryRewriter
from app.core.metrics import GENERATION_DURATION_SECONDS

logger = logging.getLogger(__name__)

class RAGService:

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.llm_provider = OllamaLLMProvider()
        self.query_writer = QueryRewriter()

    def ask(
            self, 
            question: str, 
            top_k: int = 2,
            history: list[dict] | None = None
    )-> dict:

        history = history or []

        rewritten_query = self.query_writer.rewrite(
            question=question,
            history=history
        )

        logger.info(
            "query_rewritten",
            extra={
                "original_question": question,
                "rewritten_query": rewritten_query
            }
        )
        
        start = time.perf_counter()

        retrieved_chunks = self.retrieval_service.search(
            query = rewritten_query,
            top_k=top_k
        )

        retrieval_ms = (
            time.perf_counter() - start
        ) * 1000

        logger.info(
            "retrieval_completed",
            extra={
                "duration_ms": round(retrieval_ms, 2),
                "result_count": len(retrieved_chunks),
                "top_k": top_k
            }
        )

        if not retrieved_chunks:
            return {
                "question": question,
                "rewritten_query": rewritten_query,
                "answer": (
                    "I don't have enough information"
                    "in the provided documents."
                ),
                "sources": []
            }

        context = self.context_builder.build(
            retrieved_chunks
        )

        history_text = "\n".join(
            f"{item['role']}: {item['content']}" for item in history
        )

        prompt = self.prompt_builder.build(
            question=question,
            context=context,
            history=history_text
        )

        # print ("Prompt length:", len(prompt))
        logger.info("Prompt length:", extra = {"length": len(prompt)})
        start = time.perf_counter()

        answer = self.llm_provider.generate(
            prompt
        )

        retrieval_ms = (
            time.perf_counter() - start
        ) * 1000
        GENERATION_DURATION_SECONDS.labels(
            model=self.llm_provider.model
        ).observe(time.perf_counter() - start)
        
        logger.info(
            "generation_completed",
            extra={
                "duration_ms": round(retrieval_ms, 2),
                "result_count": len(retrieved_chunks),
                "top_k": top_k
            }
        )
        
        sources = []

        seen = set()

        print("Retrieved chunks:", len(retrieved_chunks))
        print("Context length:", len(context))
        print("Prompt length:", len(prompt))

        for item in retrieved_chunks:
            metadata = item["metadata"]

            key = (
                metadata["filename"],
                metadata["chunk_index"]
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "filename": metadata["filename"],
                    "document_id": metadata.get("document_id"),
                    "chunk_index": metadata["chunk_index"],
                    "retrieval_distance": item.get("retrieval_distance"),
                    "rerank_score": item.get("rerank_score")
                }
            )

        return {
                "question": question,
                "rewritten_query": rewritten_query,
                "answer": answer, 
                "sources": sources
        }

