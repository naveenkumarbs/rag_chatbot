# RAG Chatbot

An end-to-end, locally runnable retrieval-augmented generation (RAG) application. Upload PDF or text documents, ask questions grounded in their contents, inspect retrieved sources, and continue conversations with persisted history.

The project combines document ingestion, embeddings and vector search, reranking, local LLM inference, a chat API and browser UI, persistent conversation storage, cache integration, and operational metrics.

## What It Does

1. **Ingests documents:** accepts PDF and UTF-8 text files, extracts text, and splits it into overlapping chunks.
2. **Creates embeddings:** uses an Ollama embedding model for document chunks and user queries.
3. **Retrieves evidence:** searches a persistent ChromaDB collection, applies a configurable distance limit, and reranks candidates with a Sentence Transformers cross-encoder.
4. **Builds a grounded prompt:** combines relevant chunks with recent conversation history. History can help rewrite follow-up questions as standalone search queries.
5. **Generates an answer:** calls an Ollama chat model with instructions to answer from retrieved documents and cite sources.
6. **Persists interactions:** stores conversations, messages, and source references in SQLite.
7. **Reports operational data:** exposes health checks and Prometheus metrics, with Redis caching integration and cache observability.

## GenAI Concepts Covered

- Retrieval-augmented generation (RAG) and grounding answers in private documents
- PDF/text parsing, character-based chunking, and chunk overlap
- Dense vector embeddings and similarity search
- Retrieval thresholds and candidate over-fetching
- Cross-encoder reranking of retrieved passages
- Context construction, prompt design, source attribution, and insufficient-evidence responses
- Conversation memory and history-aware query rewriting
- Local inference for embedding and text-generation models
- Embedding caching, retrieval-cache support, and latency/cache metrics

## Technology

| Area | Technology | Use |
| --- | --- | --- |
| Language and API | Python, FastAPI, Pydantic | Application services, HTTP endpoints, request validation, and interactive API docs |
| LLM and embeddings | Ollama, HTTPX | Local model inference through Ollama's HTTP API |
| Vector storage | ChromaDB | Persistent chunk embeddings and similarity search |
| Reranking | Sentence Transformers (`cross-encoder/ms-marco-MiniLM-L6-v2`) | Scores query/chunk pairs and reorders retrieval candidates |
| Relational storage | SQLite | Conversations, messages, source references, and document records |
| Cache | Redis | Embedding cache and retrieval-cache hooks |
| Document processing | pypdf, Python standard library | PDF extraction and UTF-8 text loading |
| Browser UI | HTML, CSS, JavaScript, Jinja2, Bootstrap 5 | Chat, conversation history, and document upload interface |
| Monitoring/logging | Prometheus client, Python JSON logger | Application metrics and structured JSON logs |

OpenTelemetry packages are listed in `requirements.txt`, but tracing/export is not configured in the current application.

## Requirements

- Python 3.10 or newer
- Ollama installed and running locally or at a reachable URL
- A chat model and an embedding model pulled into Ollama
- Redis is recommended for cache operation. The app can run without Redis, but `/health` will report a degraded status while Redis is unavailable.
- Internet access during dependency installation; the cross-encoder model may also download the first time reranking is initialized.

Example Ollama models (choose models appropriate for your machine):

```text
llama3.2             # chat model example
nomic-embed-text     # embedding model example
```

Pull them before starting the app:

```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

The model names in `.env` must match models available in Ollama. Keep the embedding model and dimensions compatible between indexing and querying a Chroma collection.

## Setup

Run commands from the repository root.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set the required values. Example for a local setup:

```dotenv
APP_NAME=RAG Chatbot
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

SQLITE_DB_PATH=data/rag_chatbot.db
CHROMA_DB_PATH=data/chroma
CHROMA_COLLECTION=documents

RAG_MAX_DISTANCE=1.15
RAG_HISTORY_MESSAGE_LIMIT=6

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_EMBEDDING_TTL=3600
REDIS_RETRIEVAL_TTL=600
```

The `APP_*`, `OLLAMA_*`, and storage settings are required. RAG and Redis settings have application defaults, but setting them explicitly makes the environment easier to understand. Ensure the configured storage paths are writable. Do not commit `.env` or credentials.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Set the same values shown above in `.env`.

## Run the Application and Support Services

Ollama remains a host service and is required for embeddings and generation. Redis, Prometheus, and Grafana can run in Docker. The Compose file starts only these support services; FastAPI and Ollama are not containerized.

From the repository root, start the Docker services:

```bash
docker compose up -d
docker compose ps
```

Redis is published on `localhost:6379`, matching the `.env` settings `REDIS_HOST=localhost` and `REDIS_PORT=6379`. Prometheus reads `monitoring/prometheus.yml` and scrapes `host.docker.internal:8000/metrics` every 15 seconds. Grafana and Prometheus share a Compose network, so configure Grafana's Prometheus data source URL as `http://prometheus:9090`.

Start the FastAPI app from the repository root with the virtual environment active. Bind to `0.0.0.0` so the Prometheus container can reach the host process:

```bash
fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

Alternatively:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The app initializes the SQLite schema at startup. ChromaDB data, uploaded files, and SQLite data persist under their configured paths.

Open:

- Browser chat UI: <http://127.0.0.1:8000/ui>
- Swagger API docs: <http://127.0.0.1:8000/docs>
- ReDoc API docs: <http://127.0.0.1:8000/redoc>
- Health status: <http://127.0.0.1:8000/health>
- Prometheus metrics: <http://127.0.0.1:8000/metrics>
- Prometheus web UI: <http://127.0.0.1:9090>
- Grafana: <http://127.0.0.1:3000>

Log in to Grafana with `admin` / `admin` on a fresh local install, then change the password. Add a Prometheus data source with URL `http://prometheus:9090` and select **Save & test**. Create a dashboard and add panels using the metrics listed in the [Data and Monitoring](#data-and-monitoring) section.

Stop the containers with `docker compose down`. This keeps the named Prometheus and Grafana data volumes; `docker compose down -v` also deletes those volumes.

## Use the Application

1. Open `/ui` and upload a `.pdf` or `.txt` file, or use the document upload endpoint.
2. Wait for ingestion: the file is parsed, chunked, embedded, and added to ChromaDB.
3. Ask a question in chat. The response includes a conversation ID and source metadata.
4. Select an existing conversation to continue it. Recent history can help resolve follow-up references.

Scanned PDFs containing only images are not OCR-processed and may yield no usable text.

## HTTP API

Interactive request schemas and responses are available at `/docs`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Basic application status |
| `GET` | `/health` | Checks SQLite, ChromaDB, Ollama, and Redis connectivity |
| `GET` | `/metrics` | Prometheus-format metrics |
| `GET` | `/ui` | Browser chat application |
| `POST` | `/documents/upload` | Upload/index a `.pdf` or `.txt` file (`multipart` field: `file`) |
| `GET` | `/documents` | List document records and ingestion status |
| `POST` | `/documents/{document_id}/reindex` | Rebuild a document's indexed chunks |
| `DELETE` | `/documents/{document_id}` | Delete its index entries, uploaded file, and document record |
| `GET` | `/search?query=...&top_k=5` | Retrieve and rerank passages without generating an answer |
| `POST` | `/chat` | Retrieve evidence, generate an answer, and persist a turn |
| `POST` | `/conversations` | Create a conversation |
| `GET` | `/conversations` | List conversations |
| `GET` | `/conversations/{conversation_id}` | Get a conversation, messages, and sources |

### Chat request

`conversation_id` is optional. Omit it to create a conversation; include it to continue an existing one. `top_k` must be between 1 and 20.

```json
{
	"question": "What is the resolution from the partners meeting?",
	"top_k": 5
}
```

Example with curl:

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
	-H "Content-Type: application/json" \
	-d '{"question":"What is the resolution from the partners meeting?","top_k":5}'
```

The response includes `conversation_id`, the original `question`, a `rewritten_query`, the generated `answer`, and `sources`. Each source identifies a filename and chunk and may include retrieval distance and reranking score.

### Upload a document

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" \
	-F "file=@./path/to/document.pdf"
```

Only `.pdf` and `.txt` files are accepted.

## Tests and Smoke Checks

`tests/` contains standalone scripts for ingestion, embeddings, retrieval, ChromaDB, chunking, and provider checks; it is not configured as a pytest suite. Scripts can call local services or modify the persistent Chroma collection. Review a script before running it and ensure its dependencies are available.

When running a script directly from `tests/`, add the repository root to Python's import path. In PowerShell:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python tests\test_llm_provider.py
```

Substitute the desired smoke-script filename. The environment variable applies to the current PowerShell session.

## Project Layout

```text
app/
	api/             FastAPI routes for chat, documents, search, and conversations
	core/            Settings, logging, Redis clients/caches, and metrics
	rag/
		chunking/      Text chunking
		embeddings/    Embedding provider integration
		generation/    Query rewriting, prompt/context building, and RAG orchestration
		ingestion/     PDF/text loading and document ingestion
		providers/     LLM provider interface and Ollama implementation
		reranking/     Cross-encoder passage reranking
		retrieval/     ChromaDB vector store and retrieval workflow
	repositories/    SQLite persistence
	services/        Health checks
static/            Browser UI JavaScript and CSS
templates/          Jinja2 HTML template
data/               Uploaded documents and persistent ChromaDB data
monitoring/         Prometheus scrape configuration
docker-compose.yml  Redis, Prometheus, and Grafana support services
tests/              Standalone smoke scripts
```

## RAG Pipeline and Defaults

- Chunk size: 1,000 characters with 200 characters of overlap.
- Retrieval over-fetches candidates (`max(top_k * 4, 8)`) before reranking.
- `RAG_MAX_DISTANCE` is the maximum accepted Chroma distance; the configured default is `1.15`.
- `RAG_HISTORY_MESSAGE_LIMIT` controls the recent messages supplied to chat; the configured default is `6`.
- A cross-encoder reranks filtered candidates. The prompt asks the LLM to answer only from evidence and cite it as `[Source N]`.
- If retrieval returns no candidates, the service returns an insufficient-information answer without calling the generation model.

These are implementation defaults, not universal tuning recommendations. Distance behavior depends on the Chroma collection's metric and should be evaluated with your documents and embedding model.

## How the Chatbot Uses These Services

For a chat request, the browser sends `POST /chat` to FastAPI. The service loads recent conversation history from SQLite, optionally rewrites the question with Ollama, embeds the query, searches ChromaDB, reranks the results, and asks Ollama to generate a grounded answer. The conversation, answer, and source references are then persisted in SQLite.

Redis sits on the embedding path: the embedding provider checks for a cached vector first, calls Ollama on a cache miss, and stores the resulting vector with a configured TTL. The app also has retrieval-cache hooks, but retrieval-cache writes currently fail because the cache setter references an undefined class setting. Redis is a performance cache, not the source of truth for documents or conversations.

The app records counters and timings in-process. Prometheus does not receive pushed events; every 15 seconds it scrapes the app's `GET /metrics` endpoint using `monitoring/prometheus.yml`. Grafana then queries Prometheus over the Compose network (`http://prometheus:9090`) and displays those time series in dashboards. Grafana is not currently configured to collect application logs; JSON logs go to the FastAPI process's standard output.

Example PromQL for a Grafana panel:

```promql
sum by (path, status_code) (rate(rag_http_requests_total[5m]))
```

## Data and Monitoring

- Uploaded files are stored under `data/documents/`.
- ChromaDB's persistent database is stored at `CHROMA_DB_PATH`.
- SQLite stores document metadata, conversations, messages, and message-source references at `SQLITE_DB_PATH`.
- Redis provides embedding-cache integration; retrieval-cache hooks are also present.
- `/metrics` includes HTTP request counts/durations, chat outcomes, document operations, cache hits/misses, retrieval/reranking durations, and generation duration by model.
- Exported metric families include `rag_http_requests_total`, `rag_http_request_duration_seconds`, `rag_chat_requests_total`, `rag_chat_failures_total`, `rag_embedding_cache_hits_total`, `rag_embedding_cache_misses_total`, `rag_retrieval_cache_hits_total`, `rag_retrieval_cache_misses_total`, `rag_retrieval_duration_seconds`, `rag_rerank_duration_seconds`, `rag_generation_duration_seconds`, and document upload/reindex/delete counters.
- Application logs are emitted as JSON to standard output. Request middleware adds an `X-Request-ID` response header.
- `monitoring/prometheus.yml` provides a scrape target and assumes Prometheus can resolve `host.docker.internal:8000`; adjust this for your environment.

Back up persistent data before deleting or rebuilding databases. Reindexing or deleting documents changes the vector collection and invalidates retrieval cache entries.

## Current Scope and Limitations

- This is a local-development/reference application, not a hardened production deployment. Authentication, authorization, rate limiting, and tenant isolation are not implemented.
- Chat generation is request/response; token streaming is not implemented.
- PDF processing extracts embedded text only; OCR is not included.
- Redis is a cache, not a replacement for ChromaDB or SQLite persistence.
- Retrieval-cache writes currently fail because the cache setter references an undefined class setting; embedding caching is separate.
- Docker Compose covers Redis, Prometheus, and Grafana only; FastAPI and Ollama remain separate host services. No cloud deployment configuration is included.
- OpenTelemetry dependencies are listed, but distributed tracing is not wired into the application.