from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.vector_store import search_similar_chunks
from backend.services.embedding import embed_text


async def retrieve_context(db: AsyncSession, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    query_embedding = await embed_text(question)
    return await search_similar_chunks(db, query_embedding, top_k=top_k)
