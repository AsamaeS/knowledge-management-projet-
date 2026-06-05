import logging
from pathlib import Path

from sqlalchemy import select

from backend.core.database import SessionLocal
from backend.database.memory_store import has_document_memory, store_chunks_memory
from backend.database.vector_store import store_chunks
from backend.models.document import Document
from backend.services.embedding import embed_texts
from backend.services.parser import chunk_text, extract_text

logger = logging.getLogger(__name__)

FIXED_PDF_PATH = Path(__file__).resolve().parents[1] / "km data" / "Knowledge Auo Experts.pdf"


async def seed_fixed_knowledge(use_database: bool) -> None:
    if not FIXED_PDF_PATH.exists():
        logger.warning("Fixed knowledge PDF not found: %s", FIXED_PDF_PATH)
        return

    filename = FIXED_PDF_PATH.name
    content = FIXED_PDF_PATH.read_bytes()
    raw_text = extract_text(filename, content)
    chunks = chunk_text(raw_text)
    if not chunks:
        logger.warning("Fixed knowledge PDF produced no text chunks: %s", FIXED_PDF_PATH)
        return

    embeddings = await embed_texts(chunks)
    metadata = {
        "source_type": "fixed_pdf",
        "source_path": str(FIXED_PDF_PATH),
    }

    if not has_document_memory(filename):
        store_chunks_memory(
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
        )
        logger.info("Seeded fixed PDF into memory: %s (%s chunks)", filename, len(chunks))

    if not use_database:
        return

    async with SessionLocal() as db:
        existing = await db.execute(select(Document.id).where(Document.filename == filename))
        if existing.scalar_one_or_none():
            return

        await store_chunks(
            db,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
        )
        await db.commit()
        logger.info("Seeded fixed PDF into database: %s (%s chunks)", filename, len(chunks))
