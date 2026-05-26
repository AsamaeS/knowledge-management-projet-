from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.config import settings
from backend.core.ai_service import AIService

# Singleton instance for AIService
_ai_service_instance = None

def get_ai_service() -> AIService:
    """Dependency injection helper for getting the AIService instance."""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService(settings)
    return _ai_service_instance

