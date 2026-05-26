from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class ChatSessionCreate(BaseModel):
    user_id: str = Field(..., description="Simple string representation of user session")

class ChatSessionResponse(BaseModel):
    session_id: UUID = Field(..., description="Unique ID representing active conversation session")


class Citation(BaseModel):
    chunk_id: Optional[UUID] = Field(None, description="UUID of source document chunk")
    document_id: UUID = Field(..., description="UUID of original document source")
    filename: str = Field(..., description="Source document file name")
    source_type: str = Field(..., description="interview | report | linkedin | analysis")
    excerpt: str = Field(..., description="Quoted content match excerpt")


class StatementLabel(BaseModel):
    text: str = Field(..., description="Target assertion text snippet")
    label: str = Field(..., description="Label category: fact | opinion | inference")


class ChatMessageRequest(BaseModel):
    session_id: UUID = Field(..., description="Conversation session ID")
    message: str = Field(..., description="User message content query")
    output_format: Optional[str] = Field("text", description="Desired framework layout: text | swot | pestel")


class ChatMessageResponse(BaseModel):
    answer: str = Field(..., description="AI response text or framework output representation")
    citations: List[Citation] = Field(default_factory=list, description="Grounding source citations list")
    output_type: str = Field("text", description="Returned layout format structure")
    confidence: float = Field(0.9, description="Confidence metric of grounded retrieval match")
    fact_vs_opinion_labels: List[StatementLabel] = Field(default_factory=list, description="Categorized fact vs opinion statement markings")


class MessageHistoryItem(BaseModel):
    role: str = Field(..., description="user | assistant")
    content: str = Field(..., description="Raw string content")
    citations: List[Citation] = Field(default_factory=list, description="Grounded source links")
    timestamp: str = Field(..., description="Creation time string")


class ChatHistoryResponse(BaseModel):
    session_id: UUID = Field(..., description="Active session ID identifier")
    user_id: str = Field(..., description="Session owner")
    messages: List[MessageHistoryItem] = Field(default_factory=list, description="Complete sequence history of messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
