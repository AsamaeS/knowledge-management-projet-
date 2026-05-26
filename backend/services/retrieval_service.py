import logging
from typing import List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.document import Document
from backend.models.chunk import DocumentChunk
from backend.models.graph import Node
from backend.core.ai_service import AIService

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self, db: AsyncSession, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service

    async def search_chunks(self, query: str, limit: int = 8) -> List[Tuple[DocumentChunk, Document]]:
        """Perform semantic search on document chunks using cosine similarity."""
        query_vector = await self.ai_service.embed(query)
        
        # Sort by cosine distance (which is 1 - cosine similarity)
        # Smaller distance means higher similarity
        stmt = (
            select(DocumentChunk, Document)
            .join(Document, Document.id == DocumentChunk.document_id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        
        res = await self.db.execute(stmt)
        return res.all()

    async def search_nodes(self, query: str, limit: int = 5) -> List[Node]:
        """Perform semantic search on knowledge graph nodes using cosine similarity."""
        query_vector = await self.ai_service.embed(query)
        
        stmt = (
            select(Node)
            .order_by(Node.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
