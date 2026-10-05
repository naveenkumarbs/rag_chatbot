from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from app.core.retrieval_cache import RetrievalCache

from app.rag.ingestion.ingestion_service import (
    IngestionService,
    ChromaVectorStore
)
from app.repositories.document_repository import DocumentRepository

from app.core.metrics import (
    DOCUMENT_UPLOADS_TOTAL,
    DOCUMENT_UPLOAD_FAILURES_TOTAL,
    DOCUMENT_REINDEX_TOTAL,
    DOCUMENT_DELETES_TOTAL
)
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("data/documents")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    extension = Path(
        file.filename 
    ).suffix.lower()

    if extension not in [".txt", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .txt and .pdf files are allowed."
        )
    document_repository = DocumentRepository()
    document_id = str(uuid4())
    stored_name = f"{document_id}_{file.filename}"
    file_path = UPLOAD_DIR / stored_name
    
    try:
        contents = await file.read()
        file_path.write_bytes(contents)
        print("Upload Document: STEP 1: creating document record")

        document_repository.create(
            document_id=document_id,
            original_filename=file.filename,
            stored_filename=stored_name,
            file_path=str(file_path)
        )

        print ("Upload Document: Step 2 setting INDEXING")
        document_repository.update_status(
            document_id=document_id,
            status="INDEXING"
        )

        service = IngestionService()

        print ("Upload Document: Step 3: start ingestion")
        result = service.ingest(
            file_path=str(file_path),
            original_filename=file.filename
        )  

        print ("Upload Document: Step 4: Ingestion Result:", result)
        if not result:
            DOCUMENT_UPLOAD_FAILURES_TOTAL.inc()
            document_repository.update_status(
                        document_id=document_id,
                        status="FAILED",
                    )
            raise HTTPException(
                status_code=500,
                detail="Document ingestion returned no result."
            )

        print("Upload Document: Step 5: setting INDEXED")
        document_repository.update_status(
            document_id=document_id,
            status="INDEXED",
            chunk_count=result["chunks"]
        )      

        print ("Upload Document: Step 6: upload complete")
        DOCUMENT_UPLOADS_TOTAL.inc()
        return {
            "status": "success",
            **result
        }
    except Exception as e: 
        DOCUMENT_UPLOAD_FAILURES_TOTAL.inc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    
@router.get("")
def list_documents():
    repository = DocumentRepository()
    return repository.list_all()

@router.delete("/{document_id}")
def delete_document(document_id: str):
    repository = DocumentRepository()
    document = repository.get(document_id)
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    try:
        vector_store = ChromaVectorStore()
        vector_store.delete_by_document_id(document_id)

        file_path = Path(document["file_path"])
        if file_path.exists():
            file_path.unlink()
        repository.delete(document_id)

        RetrievalCache.clear_all()
        DOCUMENT_DELETES_TOTAL.inc()
        return {
            "status": "deleted",
            "document_id": document_id
        }
    except Exception as exc:
        raise HTTPException (
            status_code=500,
            detail=str(exc)
        )

@router.post("/{document_id}/reindex")
def reindex_document(document_id:str):
    repository = DocumentRepository()
    document = repository.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document Not Found"
        )
    file_path = Path(document["file_path"])

    if not file_path.exists():
        raise HTTPException(
            status=404,
            detail="Source file not found"
        )

    try:
        repository.update_status(document_id, "INDEXING")
        vector_store = ChromaVectorStore()
        vector_store.delete_by_document_id(document_id)

        service = IngestionService()
        result = service.ingest(
            file_path=str(file_path),
            original_filename=document["original_filename"],
            document_id=document_id
        )

        print ("Reindex ingestion result:", result)
        chunk_count = result.get("chunks")

        if chunk_count is None:
            raise RuntimeError(
                f"Ingestion result does not contain "
                f"'chunks': {result}"
            )

        repository.update_status(
            document_id=document_id,
            status="REINDEXDED",
            chunk_count=chunk_count
        )

        RetrievalCache.clear_all()
        DOCUMENT_REINDEX_TOTAL.inc()
        return {
            "status": "reindexed",
            "document_id": document_id,
            "chunks": result["chunks"]
        }
    
    except Exception as exc:
        repository.update_status(
            document_id,
            "FAILED"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
    

