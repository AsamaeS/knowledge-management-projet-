import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.dependencies import get_ai_service
from backend.core.ai_service import AIService
from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSessionResponse, ChatHistoryResponse, MessageHistoryItem
from backend.services.chat_service import ChatService
from backend.models.chat import ChatSession

router = APIRouter()

@router.post("/session", response_model=ChatSessionResponse)
async def create_chat_session(db: AsyncSession = Depends(get_db)):
    """Initialize a new chat conversation session."""
    session = ChatSession(user_id="default_user", messages=[])
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return ChatSessionResponse(session_id=session.id)

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Process user message using RAG context retrieval and LLM synthesis."""
    # Check if session exists
    session = await db.get(ChatSession, request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {request.session_id} not found."
        )
        
    chat_svc = ChatService(db, ai_service)
    response = await chat_svc.answer(request)
    
    # Update messages in db
    new_user_msg = {
        "role": "user",
        "content": request.message,
        "citations": [],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    new_assistant_msg = {
        "role": "assistant",
        "content": response.answer,
        "citations": [cit.model_dump() for cit in response.citations],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Append to existing array in DB
    updated_messages = list(session.messages) + [new_user_msg, new_assistant_msg]
    session.messages = updated_messages
    await db.commit()
    
    return response

@router.get("/session/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch complete message history and citations for a conversation session."""
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found."
        )
        
    # Translate DB messages to schema items
    history = []
    for msg in session.messages:
        history.append(MessageHistoryItem(
            role=msg["role"],
            content=msg["content"],
            citations=msg.get("citations") or [],
            timestamp=msg["timestamp"]
        ))
        
    return ChatHistoryResponse(
        session_id=session.id,
        user_id=session.user_id,
        messages=history,
        created_at=session.created_at,
        updated_at=session.updated_at
    )
