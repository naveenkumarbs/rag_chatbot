import hashlib 
import json

from app.core.redis_client import redis_client
from app.core.config import settings

class EmbeddingCache:
    @staticmethod
    def _build_key(model: str, text: str) -> str:
        normalized_text = text.strip()
        text_hash=hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

        return (
            f"embedding:"
            f"{model}:"
            f"{text_hash}"
        )
    @classmethod
    def get(cls, model:str, text:str) -> list[float] | None :
        try:
            key = cls._build_key(model=model, text=text)
            cached_value = redis_client.get(key)

            if cached_value is None:
                return None

            return json.loads(cached_value)
        except Exception as exc:
            print ("Redis cache GET failed", exc)
            return None

    @classmethod
    def set(cls, model: str, text: str, embedding: list[float]) -> None:
        try:
            key = cls._build_key(model=model, text=text)
            redis_client.set(key, json.dumps(embedding), ex=settings.redis_embedding_ttl)
        except Exception as exc:
            print ("Redis cache SET failed:", exc)