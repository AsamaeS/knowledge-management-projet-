from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class DocumentBase(BaseModel):
    filename: str = Field(..., description="Name of the uploaded file")
    source_type: str = Field(..., description="Type of the source (interview, report, linkedin, analysis)")
    author: Optional[str] = Field(None, description="Author of the document")
    doc_date: Optional[str] = Field(None, description="Document creation/publication date (YYYY-MM-DD)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom provenance metadata")

class DocumentCreate(DocumentBase):
    raw_text: str = Field(..., description="Raw text extracted from the document")

class DocumentResponse(DocumentBase):
    id: UUID = Field(..., description="Unique ID of the document")
    created_at: datetime = Field(..., description="Ingestion timestamp")
    
    model_config = ConfigDict(from_attributes=True)

class IngestionResponse(BaseModel):
    document_id: UUID = Field(..., description="Unique ID of the ingested document")
    chunk_count: int = Field(..., description="Number of text chunks created")
    entities_extracted: int = Field(..., description="Number of knowledge graph nodes extracted")
    edges_created: int = Field(..., description="Number of knowledge graph relationships created")
