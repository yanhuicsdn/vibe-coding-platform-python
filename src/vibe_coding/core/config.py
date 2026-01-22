"""
Configuration management using Pydantic Settings
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Application
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://vibe_admin:vibe_admin_password@localhost:5432/vibe_platform",
        description="Database connection URL",
    )

    # Hasura
    hasura_graphql_url: str = Field(
        default="http://localhost:8080", description="Hasura GraphQL URL"
    )
    hasura_admin_secret: str = Field(
        default="change_me", description="Hasura admin secret"
    )

    # JWT
    jwt_secret: str = Field(
        default="change_me_minimum_32_characters_long", description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=10080, description="JWT expiration in minutes (7 days)")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )

    # AI Safety
    ai_schema_change_enabled: bool = Field(default=True, description="Enable AI schema changes")
    ai_max_fields_per_entity: int = Field(default=50, description="Max fields per entity")
    ai_max_entities_per_project: int = Field(default=100, description="Max entities per project")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Try to parse as JSON list
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Split by comma if not JSON
                return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() in ("development", "dev")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() in ("production", "prod")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
