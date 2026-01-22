"""
Authentication and authorization models
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User roles"""

    ADMIN = "admin"
    USER = "user"
    AI_AGENT = "ai_agent"


class TokenPayload(BaseModel):
    """JWT token payload"""

    user_id: str = Field(..., description="User ID")
    tenant_id: str = Field(..., description="Tenant ID")
    project_id: str | None = Field(default=None, description="Project ID")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    iat: int | None = Field(default=None, description="Issued at")
    exp: int | None = Field(default=None, description="Expiration time")


class LoginRequest(BaseModel):
    """Login request"""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")


class RegisterRequest(BaseModel):
    """Registration request"""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    name: str = Field(..., min_length=2, description="User name")
    tenant_name: str | None = Field(default=None, description="Tenant name (for new tenant)")


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str | None = Field(default=None, description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int | None = Field(default=None, description="Expiration in seconds")


class User(BaseModel):
    """User information"""

    id: str = Field(..., description="User UUID")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User name")
    tenant_id: str = Field(..., description="Tenant UUID")
    role: UserRole = Field(..., description="User role")
    created_at: str = Field(..., description="Creation timestamp")


class AuthResponse(BaseModel):
    """Authentication response"""

    token: TokenResponse = Field(..., description="Token information")
    user: User = Field(..., description="User information")


class Tenant(BaseModel):
    """Tenant information"""

    id: str = Field(..., description="Tenant UUID")
    name: str = Field(..., description="Tenant name")
    owner_user_id: str = Field(..., description="Owner user ID")
    settings: dict[str, Any] | None = Field(default=None, description="Tenant settings")
    created_at: str = Field(..., description="Creation timestamp")


class Project(BaseModel):
    """Project information"""

    id: str = Field(..., description="Project UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    name: str = Field(..., description="Project name")
    description: str | None = Field(default=None, description="Project description")
    schema_version: str = Field(..., description="Current schema version")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")


class HasuraJWTClaims(BaseModel):
    """Hasura JWT claims structure"""

    sub: str = Field(..., description="Subject (user ID)")
    https://hasura.io/jwt/claims: dict[str, Any] = Field(..., description="Hasura-specific claims")
