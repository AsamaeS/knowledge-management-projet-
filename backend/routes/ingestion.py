from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.database.memory_store import store_chunks_memory
from backend.database.vector_store import store_chunks
from backend.services.embedding import embed_texts
from backend.services.parser import extract_text, chunk_text

router = APIRouter()


@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        content = await file.read()
        raw_text = extract_text(file.filename or "upload", content)
        chunks = chunk_text(raw_text)
        if not chunks:
            raise ValueError("No text could be extracted from the uploaded file.")

        embeddings = await embed_texts(chunks)
        filename = file.filename or "upload"
        try:
            document = await store_chunks(
                db,
                filename=filename,
                chunks=chunks,
                embeddings=embeddings,
                metadata={"content_type": file.content_type},
            )
            await db.commit()
            document_id = document.id
        except Exception:
            await db.rollback()
            document = store_chunks_memory(
                filename=filename,
                chunks=chunks,
                embeddings=embeddings,
                metadata={"content_type": file.content_type},
            )
            document_id = document["id"]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "document_id": document_id,
        "filename": file.filename or "upload",
        "chunk_count": len(chunks),
    }
