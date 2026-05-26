from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.config import settings

# Create async engine
# Note: we use pool_pre_ping to ensure connection health
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Declarative base for ORM models
Base = declarative_base()

async def get_db():
    """Dependency for acquiring database sessions in FastAPI routes."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

from sqlalchemy import text

async def init_db():
    """Create extension pgvector and all tables."""
    # Import all models to ensure they are registered on Base
    from backend.models import Document, DocumentChunk, Node, Edge, Scenario, ScenarioStep, SimulationSession, ChatSession
    
    async with engine.begin() as conn:
        # Create pgvector extension if it does not exist
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


