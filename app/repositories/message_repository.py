from datetime import datetime, timezone
from uuid import uuid4 

from app.repositories.database import get_connection

class MessageRepository:
    def create(self, conversation_id: str, role: str, content: str) -> dict: 
        if not conversation_id:
            raise ValueError(
                "conversation_id is required when creating a message."
            )
        message_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
    
        connection = get_connection()

        try:
            connection.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    now
                )
            )

            connection.execute(
                """
                UPDATE conversations SET updated_at = ? WHERE id = ?
                """,
                (
                    now,
                    conversation_id
                )
            )

            connection.commit()

        finally:
            connection.close()

        return {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": now
        }

    def list_by_conversation(self, conversation_id: str) -> list[dict]:
        connection = get_connection()
        try:
            rows = connection.execute(
                """
                SELECT * FROM messages WHERE
                conversation_id = ?
                ORDER BY created_at ASC
                """,
                (
                    conversation_id,
                )
            ).fetchall()
        finally:
            connection.close()

        return [dict(row) for row in rows]

    def get_recent(self, conversation_id: str, limit: int = 6) -> list[dict]:
        connection = get_connection()
        try:
            rows = connection.execute(
                """
                SELECT * 
                FROM messages
                WHERE conversation_id=?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (conversation_id, limit,)
            ).fetchall()
        finally:
            connection.close()
        messages = [
            dict(row) for row in rows
        ]

        messages.reverse()

        return messages