import hashlib
import math
from typing import List

from backend.config import settings


async def embed_text(text: str) -> List[float]:
    vectors = await embed_texts([text])
    return vectors[0]


async def embed_texts(texts: List[str]) -> List[List[float]]:
    if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return await _openai_embeddings(texts)

    return [_local_stub_embedding(text, settings.EMBEDDING_DIMENSION) for text in texts]


async def _openai_embeddings(texts: List[str]) -> List[List[float]]:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def _local_stub_embedding(text: str, dimension: int) -> List[float]:
    vector = [0.0] * dimension
    tokens = text.lower().split()

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
