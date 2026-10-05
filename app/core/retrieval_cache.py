import hashlib 
import json

from app.core.redis_client import redis_client
from app.core.config import settings

class RetrievalCache:

    @staticmethod
    def _build_key(query:str, candidate_k:int) -> str:
        normalized = query.strip()

        query_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        return (
            f"retrieval:"
            f"k{candidate_k}:"
            f"{query_hash}"
        )
    @classmethod
    def get(cls, query:str, candidate_k: int) -> list[dict] | None :
        try:
            key = cls._build_key(query=query, candidate_k=candidate_k)

            value = redis_client.get(key)

            if value is None:
                return None
            return json.loads(value)
        except Exception as exc:
            print ("Redis retrieval cache GET failed:", exc)
            return None

    @classmethod
    def set(cls, query:str, candidate_k: int, candidates: list[dict]) -> None :
        try:
            key = cls._build_key(query=query, candidate_k=candidate_k)
            redis_client.set(key, json.dumps(candidates), ex=cls.settings.redis_retrieval_ttl)
        except Exception as exc:
            print ("Redis retrieval cache failed:", exc)

    @classmethod
    def clear_all(cls) -> None:
        try:
            for key in redis_client.scan_iter(match="retrieval:*"):
                redis_client.delete(key)
        except Exception as exc:
            print("Retrieval cache clear failed:", exc)

