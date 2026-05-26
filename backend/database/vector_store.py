from typing import Any, Dict, List, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chunk import DocumentChunk
from backend.models.document import Document
from backend.database.memory_store import list_chunk_vectors_memory, search_similar_chunks_memory


async def store_chunks(
    db: AsyncSession,
    *,
    filename: str,
    chunks: Sequence[str],
    embeddings: Sequence[Sequence[float]],
    metadata: Dict[str, Any] | None = None,
) -> Document:
    document = Document(
        filename=filename,
        source_type="report",
        raw_text="\n\n".join(chunks),
        metadata_={"source_file": filename, **(metadata or {})},
    )
    db.add(document)
    await db.flush()

    for index, chunk in enumerate(chunks):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=list(embeddings[index]),
                metadata_={"source_file": filename},
                token_count=len(chunk.split()),
            )
        )

    await db.flush()
    return document


async def search_similar_chunks(
    db: AsyncSession,
    query_embedding: Sequence[float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.content,
            DocumentChunk.metadata_,
            Document.filename,
            Document.id.label("document_id"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(DocumentChunk.embedding.cosine_distance(list(query_embedding)))
        .limit(top_k)
    )
    try:
        rows = (await db.execute(stmt)).mappings().all()
    except Exception:
        await db.rollback()
        return search_similar_chunks_memory(query_embedding, top_k=top_k)

    return [
        {
            "id": row["id"],
            "document_id": row["document_id"],
            "text": row["content"],
            "metadata": row["metadata_"] or {"source_file": row["filename"]},
            "source": row["filename"],
        }
        for row in rows
    ]


async def list_chunk_vectors(db: AsyncSession, limit: int = 200) -> List[Dict[str, Any]]:
    stmt = (
        select(DocumentChunk.id, DocumentChunk.content, DocumentChunk.embedding, DocumentChunk.metadata_, Document.filename)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(DocumentChunk.created_at.desc())
        .limit(limit)
    )
    try:
        rows = (await db.execute(stmt)).mappings().all()
    except Exception:
        await db.rollback()
        return list_chunk_vectors_memory(limit=limit)

    return [
        {
            "id": row["id"],
            "text": row["content"],
            "embedding": list(row["embedding"]),
            "metadata": row["metadata_"] or {"source_file": row["filename"]},
        }
        for row in rows
    ]


async def get_chunk(db: AsyncSession, chunk_id: UUID) -> DocumentChunk | None:
    return await db.get(DocumentChunk, chunk_id)
