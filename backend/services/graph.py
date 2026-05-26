import math
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.vector_store import list_chunk_vectors


async def build_chunk_graph(
    db: AsyncSession,
    threshold: float = 0.75,
    limit: int = 200,
) -> Dict[str, List[Dict[str, Any]]]:
    chunks = await list_chunk_vectors(db, limit=limit)
    adjacency: Dict[str, List[Dict[str, Any]]] = {str(chunk["id"]): [] for chunk in chunks}

    for left_index, left in enumerate(chunks):
        for right in chunks[left_index + 1:]:
            score = _cosine(left["embedding"], right["embedding"])
            if score >= threshold:
                left_id = str(left["id"])
                right_id = str(right["id"])
                adjacency[left_id].append({"target": right_id, "similarity": score})
                adjacency[right_id].append({"target": left_id, "similarity": score})

    return adjacency


def _cosine(left: List[float], right: List[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
