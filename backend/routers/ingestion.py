from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.core.database import get_db
from backend.core.dependencies import get_ai_service
from backend.core.ai_service import AIService
from backend.schemas.document import IngestionResponse, DocumentResponse
from backend.services.ingestion_service import IngestionService
from backend.models.document import Document
from backend.models.chunk import DocumentChunk
from backend.models.graph import Node, Edge

router = APIRouter()

@router.post("/ingest/file", response_model=IngestionResponse)
async def ingest_single_file(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    author: Optional[str] = Form(None),
    doc_date: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Ingest a single document, parse it, index text chunks, and extract graph entities."""
    if source_type not in ["interview", "report", "linkedin", "analysis"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_type must be one of: interview, report, linkedin, analysis"
        )
        
    ingest_svc = IngestionService(db, ai_service)
    try:
        result = await ingest_svc.ingest_file(
            file=file,
            source_type=source_type,
            author=author,
            doc_date=doc_date
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )

@router.post("/ingest/batch", response_model=List[IngestionResponse])
async def ingest_batch_files(
    files: List[UploadFile] = File(...),
    source_type: str = Form(...),
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Ingest a batch of files under a single source type category."""
    if source_type not in ["interview", "report", "linkedin", "analysis"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_type must be one of: interview, report, linkedin, analysis"
        )
        
    ingest_svc = IngestionService(db, ai_service)
    results = []
    
    for file in files:
        try:
            res = await ingest_svc.ingest_file(
                file=file,
                source_type=source_type
            )
            results.append(res)
        except Exception as e:
            # We log and keep going in a batch to avoid breaking everything
            import logging
            logging.getLogger(__name__).error(f"Batch file ingestion failed for {file.filename}: {e}")
            
    return results

@router.get("/ingest/status/{document_id}")
async def get_ingestion_status(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve indexing statistics and extraction metadata for an ingested document."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
        
    # Get chunk counts
    chunk_count_query = await db.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)
    )
    chunk_count = chunk_count_query.scalar() or 0

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "source_type": doc.source_type,
        "status": "completed",
        "chunk_count": chunk_count,
        "ingested_at": doc.created_at
    }

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a paginated list of all ingested documents in the platform."""
    query = select(Document).order_by(Document.created_at.desc()).offset(offset).limit(limit)
    res = await db.execute(query)
    documents = res.scalars().all()
    return documents
