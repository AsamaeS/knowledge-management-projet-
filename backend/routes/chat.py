from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.core.database import get_db
from backend.services.retrieval import retrieve_context

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    chunks = await retrieve_context(db, request.question, top_k=request.top_k)
    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}" for chunk in chunks
    )
    answer = await _answer_question(request.question, context)

    return {
        "answer": answer,
        "sources": sorted({chunk["source"] for chunk in chunks}),
    }


async def _answer_question(question: str, context: str) -> str:
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer using only the provided context. "
                        "If the answer is not in the context, say you do not know."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question:\n{question}\n\nContext:\n{context}",
                },
            ],
        )
        return response.choices[0].message.content or ""

    if not context:
        return "I do not know based on the current knowledge base."

    return (
        "Local stub answer: I found relevant context in the knowledge base, "
        "but no LLM provider is configured. Retrieved context:\n\n"
        f"{context[:2000]}"
    )
