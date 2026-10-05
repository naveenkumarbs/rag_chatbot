from app.rag.ingestion.ingestion_service import (
    IngestionService
)

service = IngestionService()

result = service.ingest(
    "data\\documents\\rag_text.txt"
)

print ("Ingestion result:", result)
