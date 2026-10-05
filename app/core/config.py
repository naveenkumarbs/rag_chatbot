from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_env: str
    app_host: str
    app_port: int

    ollama_base_url: str
    ollama_chat_model: str
    ollama_embedding_model: str

    sqlite_db_path: str
    chroma_db_path: str
    chroma_collection: str

    rag_max_distance: float = 1.15
    rag_history_message_limit: int = 6

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    redis_embedding_ttl: int = 3600
    redis_retrieval_ttl: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()