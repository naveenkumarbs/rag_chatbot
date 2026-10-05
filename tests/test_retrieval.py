from app.rag.retrieval.retrieval_service import (
    RetrievalService
)

service = RetrievalService()

results = service.search(
    query = "How does RAG use private documents?",
    top_k = 3
)

for result in results:
    print ("\n----------------------")
    print ("Distance:", result["distance"])
    print ("Source:", result["metadata"]["filename"])
    print ("Text:")
    print (result["text"])