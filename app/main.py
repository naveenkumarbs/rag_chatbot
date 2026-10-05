import logging 
import time 
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager

from app.repositories.database import initialize_database
from app.core.logging_config import configure_logging
from app.core.config import settings
from app.services.health_service import (
    check_chroma,
    check_ollama,
    check_sqlite,
    check_redis,
)

from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router 
from app.api.conversations import router as conversations_router
from fastapi.responses import Response 
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.metrics import (
    HTTP_REQUEST_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    initialize_database()
    yield

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")

app.include_router(documents_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(conversations_router)

@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/")
def root():
    return {
        "application": settings.app_name,
        "status": "running",
        "environment": settings.app_env
    }


@app.get("/health")
def health():
    services = {
        "sqlite": check_sqlite(),
        "chroma": check_chroma(),
        "ollama": check_ollama(),
        "redis": check_redis()
    }

    healthy = all(services.values())

    return {
        "status": "healthy" if healthy else "degraded",
        "services": services
    }

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next
):
    request_id = str(uuid4())

    start = time.perf_counter()

    try:
        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - start
        ) * 1000

        logger.info(
            "http_request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response

    except Exception:
        logger.exception(
            "http_request_failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path
            }
        )
        raise

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    start = time.perf_counter()

    try:
        response = await call_next(request)

        duration = (time.perf_counter() - start)

        HTTP_REQUEST_TOTAL.labels(
            method = request.method,
            path = request.url.path,
            status_code=response.status_code
        ).inc() 

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method = request.method,
            path = request.url.path
        ).observe(duration)

        logger.info(
            "http_request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(
                    duration * 1000, 2
                )
            }
        )

        response.headers["X-Request-ID"] = request_id

        return response
    except Exception:
        HTTP_REQUEST_TOTAL.labels(
            method=request.method,
            path=request.url.path,
            status_code=500
        ).inc()

        logger.exception(
            "http_request_failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path
            }
        )

        raise
    

