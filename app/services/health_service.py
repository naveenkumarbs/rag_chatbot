import sqlite3

import chromadb
import httpx

from app.core.config import settings

from app.core.redis_client import redis_client

def check_sqlite() -> bool:
    try:
        connection = sqlite3.connect(settings.sqlite_db_path)
        connection.execute("SELECT 1")
        connection.close()
        return True
    except Exception:
        return False


def check_chroma() -> bool:
    try:
        client = chromadb.PersistentClient(
            path=settings.chroma_db_path
        )
        client.heartbeat()
        return True
    except Exception:
        return False


def check_ollama() -> bool:
    try:
        response = httpx.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False

def check_redis() -> bool:
    try:
        return bool(redis_client.ping())
    except Exception:
        return False