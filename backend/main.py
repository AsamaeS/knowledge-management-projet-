import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.core.database import get_db, init_db
from backend.routes.chat import router as chat_router
from backend.routes.ingestion import router as ingestion_router
from backend.services.graph import build_chunk_graph

logger = logging.getLogger(__name__)

app = FastAPI(title="NEXUS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup() -> None:
    try:
        await init_db()
    except Exception as exc:
        logger.warning("Database unavailable; running with in-memory fallback: %s", exc)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/graph/chunks")
async def chunk_graph(
    threshold: float = 0.75,
    limit: int = 200,
    db: AsyncSession = Depends(get_db),
):
    return await build_chunk_graph(db, threshold=threshold, limit=limit)
