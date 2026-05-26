import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Date, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from backend.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    source_type = Column(
        Enum("interview", "report", "linkedin", "analysis", name="source_type_enum"),
        nullable=False
    )
    author = Column(String, nullable=True)
    doc_date = Column(Date, nullable=True)
    raw_text = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
