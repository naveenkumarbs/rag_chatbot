from prometheus_client import Counter, Histogram

HTTP_REQUEST_TOTAL = Counter(
    "rag_http_requests_total",
    "Total number of HTTP requests",
    ["method","path","status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram (
    "rag_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"]
)

CHAT_REQUESTS_TOTAL = Counter(
    "rag_chat_requests_total",
    "Total number of chat requests"
)

CHAT_FAILURES_TOTAL = Counter(
    "rag_chat_failures_total",
    "Total number of failed chat requests"
)

EMBEDDING_CACHE_HITS_TOTAL = Counter (
    "rag_embedding_cache_hits_total",
    "Embedding cache hits"
)

EMBEDDING_CACHE_MISSES_TOTAL = Counter (
    "rag_embedding_cache_misses_total",
    "Embedding cache misses"
)

RETRIEVAL_CACHE_HITS_TOTAL = Counter (
    "rag_retrieval_cache_hits_total",
    "Retrieval cache hits"
)

RETRIEVAL_CACHE_MISSES_TOTAL = Counter (
    "rag_retrieval_cache_misses_total",
    "Retrieval cache misses"
)

RETRIEVAL_DURATION_SECONDS = Histogram (
    "rag_retrieval_duration_seconds",
    "RAG retrieval duration in seconds"
)

RERANK_DURATION_SECONDS = Histogram (
    "rag_rerank_duration_seconds",
    "Reranking duration in seconds"
)

GENERATION_DURATION_SECONDS = Histogram (
    "rag_generation_duration_seconds",
    "LLM generation duration in seconds",
    ["model"]
)

DOCUMENT_UPLOADS_TOTAL = Counter (
    "rag_document_uploads_total",
    "Successful document uploads"
)

DOCUMENT_UPLOAD_FAILURES_TOTAL = Counter (
    "rag_document_upload_failures_total",
    "Failed document uploads"
)

DOCUMENT_REINDEX_TOTAL = Counter (
    "rag_document_reindex_total",
    "Successful document reindex operations"
)

DOCUMENT_DELETES_TOTAL = Counter (
    "rag_document_deletes_total",
    "Successful document deletions"
)
