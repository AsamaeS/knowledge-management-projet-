import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
from backend.core.database import Base
from backend.config import settings

class Node(Base):
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # 'person','company','theme','concept','insight'
    description = Column(Text, nullable=True)
    source_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    properties = Column(JSON, nullable=False, default=dict)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Edge(Base):
    __tablename__ = "edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    relation = Column(String, nullable=False, index=True)  # 'works_at','mentions','related_to','opposes'
    weight = Column(Float, nullable=False, default=1.0)
    source_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    properties = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
