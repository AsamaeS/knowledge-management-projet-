from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector

from .core.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    # 1536-dim embedding for OpenAI text-embedding-3-small (adjust if using other model)
    embedding = Column(Vector(1536), nullable=False)
