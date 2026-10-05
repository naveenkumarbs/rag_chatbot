import sqlite3
from pathlib import Path 

from app.core.config import settings 

def get_connection() -> sqlite3.Connection:
    db_path = Path(settings.sqlite_db_path)

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(db_path, check_same_thread=False)

    connection.row_factory = sqlite3.Row

    return connection

def initialize_database() -> None:
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL, 
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at  TEXT NOT NULL,

                FOREIGN KEY (conversation_id)
                    REFERENCES converstaions(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS message_sources (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                document_id TEXT,
                chunk_index INTEGER,
                distance REAL,

                FOREIGN KEY (message_id)
                    REFERENCES messages(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                chunk_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS
            idx_messages_conversation_id ON messages(conversation_id);

            CREATE INDEX IF NOT EXISTS
            idx_message_sources_message_id 
            ON message_sources(message_id);
            """
        )

        # migration helper for message_sources
        columns = connection.execute(
            "PRAGMA table_info(message_sources)"
        ).fetchall()

        column_names = {
            row[1] for row in columns
        }

        if "retrieval_distance" not in column_names:
            connection.execute(
                """
                ALTER TABLE message_sources
                ADD COLUMN retrieval_distance REAL
                """
            )

        if "rerank_score" not in column_names:
            connection.execute(
                """
                ALTER TABLE message_sources
                ADD COLUMN rerank_score REAL
                """
            )

        connection.commit()

    finally:
        connection.close()
