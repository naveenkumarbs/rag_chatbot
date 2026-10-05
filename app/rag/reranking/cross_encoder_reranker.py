from sentence_transformers import CrossEncoder

from app.rag.reranking.base import Reranker

class CrossEncoderReranker(Reranker):
    def __init__(self):
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    def rerank(self, query:str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []
        pairs = [(query, item["text"]) for item in candidates]
        scores = self.model.predict(pairs)
        for item, score in zip(candidates, scores):
            item['rerank_score'] = float(score)
        candidates.sort(key=lambda item:item["rerank_score"], reverse=True)
        print("\nRERANK RESULTS")
        for item in candidates:
            print(
                item["metadata"]["filename"],
                "retrieval=",
                round(
                    item["retrieval_distance"], 4
                ),
                "rerank=",
                round(
                    item["rerank_score"], 4
                )
            )
            best_score = candidates[0]["rerank_score"]
            RERANK_SCORE_MARGIN = 2.0
            relevant = [
                item for item in candidates if item["rerank_score"] >= best_score - RERANK_SCORE_MARGIN
            ]
        return relevant[:top_k]