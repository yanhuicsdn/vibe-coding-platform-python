"""
Schema management and deployment models
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Intent types for AI parsing"""

    CREATE_ENTITY = "create_entity"
    UPDATE_ENTITY = "update_entity"
    DELETE_ENTITY = "delete_entity"
    ADD_FIELD = "add_field"
    UPDATE_FIELD = "update_field"
    DELETE_FIELD = "delete_field"
    SET_PERMISSION = "set_permission"
    CREATE_RELATIONSHIP = "create_relationship"
    DELETE_RELATIONSHIP = "delete_relationship"


class ParsedIntent(BaseModel):
    """Parsed intent from natural language"""

    type: IntentType = Field(..., description="Intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    entities: dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    operations: list[Any] = Field(default_factory=list, description="Parsed operations")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")


class SchemaDeploymentResult(BaseModel):
    """Schema deployment result"""

    success: bool = Field(..., description="Whether deployment succeeded")
    version: str = Field(..., description="Deployed schema version")
    migration_id: str = Field(..., description="Migration UUID")
    changes: dict[str, list[str]] = Field(default_factory=dict, description="Applied changes")
    errors: list[str] | None = Field(default=None, description="Error messages")
    warnings: list[str] | None = Field(default=None, description="Warning messages")


class RollbackResult(BaseModel):
    """Rollback operation result"""

    success: bool = Field(..., description="Whether rollback succeeded")
    previous_version: str = Field(..., description="Previous schema version")
    migration_ids: list[str] = Field(default_factory=list, description="Rolled back migrations")
    errors: list[str] | None = Field(default=None, description="Error messages")


class VersionInfo(BaseModel):
    """Schema version information"""

    version: str = Field(..., description="Version number")
    migration_id: str = Field(..., description="Migration UUID")
    schema: dict[str, Any] = Field(..., description="Schema snapshot")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="Creator user ID")
    is_rollback_point: bool = Field(default=False, description="Whether marked as rollback point")


class VersionState(BaseModel):
    """Version state for a project"""

    project_id: str = Field(..., description="Project UUID")
    current_version: str = Field(..., description="Current version")
    versions: list[VersionInfo] = Field(default_factory=list, description="Version history")


class SystemHealth(BaseModel):
    """System health status"""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Overall status")
    components: dict[str, Literal["healthy", "unhealthy"]] = Field(
        default_factory=dict, description="Component health"
    )
    timestamp: str = Field(..., description="Check timestamp")


class HasuraPermissionFilter(BaseModel):
    """Hasura permission filter"""

    and_condition: list[Any] | None = Field(default=None, alias="and", description="AND conditions")
    or_condition: list[Any] | None = Field(default=None, alias="or", description="OR conditions")
    not_condition: Any | None = Field(default=None, alias="not", description="NOT condition")

    model_config = {"populate_by_name": True}


class HasuraTablePermission(BaseModel):
    """Hasura table permission"""

    filter: dict[str, Any] | None = Field(default=None, description="Row filter")
    check: dict[str, Any] | None = Field(default=None, description="Insert check")
    set: dict[str, Any] | None = Field(default=None, description="Insert set values")
    columns: list[str] | None = Field(default=None, description="Allowed columns")
    allow_aggregations: bool = Field(default=False, description="Allow aggregations")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Check timestamp")
    service: str = Field(default="backend-controller", description="Service name")


class APIResponse(BaseModel):
    """Standard API response"""

    success: bool = Field(..., description="Request success status")
    data: Any | None = Field(default=None, description="Response data")
    error: str | None = Field(default=None, description="Error message")
    warnings: list[str] | None = Field(default=None, description="Warning messages")
