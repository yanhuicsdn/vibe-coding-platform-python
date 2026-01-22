"""
Main FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vibe_coding.api.routes import health, schema, intent
from vibe_coding.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    settings = get_settings()
    print(f"🚀 Starting Vibe Coding Platform Backend")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")
    print(f"   Hasura: {settings.hasura_graphql_url}")

    yield

    # Shutdown
    print("👋 Shutting down Vibe Coding Platform Backend")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title="Vibe Coding Platform",
        description="Multi-tenant Hasura Backend Support System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(schema.router, prefix="/api/v1", tags=["Schema"])
    app.include_router(intent.router, prefix="/api/v1", tags=["Intent"])

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "vibe_coding.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
