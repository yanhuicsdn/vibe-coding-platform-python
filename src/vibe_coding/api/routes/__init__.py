"""
API Routes Package
"""

from vibe_coding.api.routes.health import router as health_router
from vibe_coding.api.routes.intent import router as intent_router
from vibe_coding.api.routes.schema import router as schema_router

__all__ = ["health_router", "schema_router", "intent_router"]
