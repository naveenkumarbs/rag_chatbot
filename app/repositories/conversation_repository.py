from datetime import datetime, timezone
from uuid import uuid4

from app.repositories.database import get_connection

class ConversationRepository:
    def create(self, title: str | None = None) -> dict:
        conversation_id = str(uuid4())

        now = datetime.now(timezone.utc).isoformat()

        connection = get_connection()

        try:
            connection.execute(
                """
                INSERT INTO conversations (
                    id,
                    title,
                    created_at, 
                    updated_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    title,
                    now,
                    now
                )
            )

            connection.commit()

        finally:
            connection.close()

        return {
            "id": conversation_id,
            "title": title,
            "created_at": now,
            "updated_at": now
        }

    def get(self, conversation_id: str) -> dict | None:
        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT * FROM conversations where id = ?
                """,
                (conversation_id,)
            ).fetchone()
        finally:
            connection.close()
        
        if row is None:
            return None
        return dict(row)

    def list_all(self) -> list[dict]:
        connection = get_connection()
        try:
            rows = connection.execute(
                """
                SELECT * FROM conversations ORDER BY updated_at DESC
                """
            ).fetchall()
        finally:
            connection.close()

        return[
            dict(row)
            for row in rows
        ]
