import math
import uuid
from datetime import datetime
from typing import Any, Dict, List, Sequence

_chunks: List[Dict[str, Any]] = []
_documents: List[Dict[str, Any]] = []


def has_document_memory(filename: str) -> bool:
    return any(document["filename"] == filename for document in _documents)


def store_chunks_memory(
    *,
    filename: str,
    chunks: Sequence[str],
    embeddings: Sequence[Sequence[float]],
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    document = {
        "id": uuid.uuid4(),
        "filename": filename,
        "metadata": {"source_file": filename, **(metadata or {})},
        "created_at": datetime.utcnow().isoformat(),
    }
    _documents.append(document)

    for index, chunk in enumerate(chunks):
        _chunks.append(
            {
                "id": uuid.uuid4(),
                "document_id": document["id"],
                "text": chunk,
                "embedding": list(embeddings[index]),
                "metadata": {"source_file": filename},
                "source": filename,
                "chunk_index": index,
            }
        )

    return document


def search_similar_chunks_memory(
    query_embedding: Sequence[float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    scored = [
        (chunk, _cosine(query_embedding, chunk["embedding"]))
        for chunk in _chunks
    ]
    scored.sort(key=lambda item: item[1], reverse=True)

    return [
        {
            "id": chunk["id"],
            "document_id": chunk["document_id"],
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "source": chunk["source"],
        }
        for chunk, _score in scored[:top_k]
    ]


def list_chunk_vectors_memory(limit: int = 200) -> List[Dict[str, Any]]:
    return _chunks[-limit:]


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
