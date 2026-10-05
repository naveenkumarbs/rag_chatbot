from datetime import datetime, timezone

from app.repositories.database import get_connection

class DocumentRepository:
    def create(
            self, 
            document_id: str,
            original_filename: str,
            stored_filename: str,
            file_path: str 
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        connection = get_connection()
        try:
            connection.execute(
                """
                INSERT INTO documents (
                    id,
                    original_filename,
                    stored_filename,
                    file_path,
                    status,
                    chunk_count,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    "UPLOADED",
                    0,
                    now,
                    now
                )
            )

            connection.commit()

        finally:
            connection.close()

        return {
            "id": document_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_path": file_path,
            "status": "UPLOADED",
            "chunk_count": 0,
            "created_at": now,
            "updated_at": now
        }

    def update_status(
            self,
            document_id: str,
            status: str,
            chunk_count: int | None = None
    ) -> None :
        now = datetime.now(timezone.utc).isoformat()
        connection = get_connection()

        try:
            if chunk_count is None:
                connection.execute(
                    """
                    UPDATE documents
                    SET status = ?,
                    updated_at = ?
                    WHERE id = ?
                    """,
                    (status, now, document_id)
                )
            else:
                connection.execute(
                    """
                    UPDATE documents
                    SET status = ?,
                        chunk_count = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (status, chunk_count, now, document_id)
                )

            connection.commit()

        finally:
            connection.close()

    def get (self, document_id: str) -> dict | None :
        connection = get_connection()
        try:
            row = connection.execute(
                """
                SELECT *
                FROM documents
                WHERE id = ?
                """,
                (document_id,)
            ).fetchone()
        finally:
            connection.close()

        return dict(row) if row else None

    def list_all(self) -> list[dict]:
        connection = get_connection()
        try:
            rows = connection.execute(
                """
                SELECT *
                FROM documents
                ORDER BY created_at DESC
                """
            ).fetchall()
        finally:
            connection.close()

        return [dict(row) for row in rows]

    def delete(self, document_id: str) -> None:
        connection = get_connection()

        try:
            connection.execute(
                """
                DELETE FROM documents
                WHERE id = ?
                """,
                (document_id,)
            )

            connection.commit()
        finally:
            connection.close()
        
