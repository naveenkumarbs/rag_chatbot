from uuid import uuid4

from app.repositories.database import get_connection


class MessageSourceRepository:

    def create_many(
        self,
        message_id: str,
        sources: list[dict]
    ) -> None:

        if not sources:
            return

        rows = []

        for source in sources:
            row = (
                str(uuid4()),
                message_id,
                source.get("filename"),
                source.get("document_id"),
                source.get("chunk_index"),
                source.get("retrieval_distance"),
                source.get("rerank_score")
            )

            rows.append(row)

        # Temporary debug
        print("Source rows:")
        for row in rows:
            print(row)
            print("Values:", len(row))

        connection = get_connection()

        try:
            connection.executemany(
                """
                INSERT INTO message_sources (
                    id,
                    message_id,
                    filename,
                    document_id,
                    chunk_index,
                    retrieval_distance,
                    rerank_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows
            )

            connection.commit()

        finally:
            connection.close()

    def list_by_message(self, message_id:str) -> list[dict]:
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    filename,
                    document_id,
                    chunk_index,
                    retrieval_distance,
                    rerank_score
                FROM message_sources
                WHERE message_id=?
                ORDER BY rerank_score DESC
                """,
                (message_id,)
            ).fetchall()

        finally:
            connection.close()

        return [dict(row) for row in rows]
    