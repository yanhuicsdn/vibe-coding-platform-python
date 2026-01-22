"""
DSL (Domain Specific Language) models using Pydantic
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class TenantMode(str, Enum):
    """Tenant isolation modes"""

    ROW_ISOLATION = "row_isolation"
    SCHEMA_ISOLATION = "schema_isolation"  # NOT IMPLEMENTED


class FieldDataType(str, Enum):
    """Supported field data types"""

    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    UUID = "uuid"
    JSON = "json"
    ARRAY = "array"


class OwnershipMode(str, Enum):
    """Entity ownership modes"""

    USER = "user"
    TENANT = "tenant"
    SHARED = "shared"


class PermissionType(str, Enum):
    """Permission types"""

    OWNER = "owner"
    TENANT = "tenant"
    PROJECT = "project"
    PUBLIC = "public"


class PermissionAction(str, Enum):
    """Permission actions"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class FieldDefinition(BaseModel):
    """Field definition in an entity"""

    name: str = Field(..., pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$", description="Field name")
    type: FieldDataType = Field(..., description="Field data type")
    required: bool = Field(default=False, description="Whether field is required")
    unique: bool = Field(default=False, description="Whether field is unique")
    default_value: Any | None = Field(default=None, description="Default value")
    nullable: bool = Field(default=True, description="Whether field can be null")
    array: bool = Field(default=False, description="Whether field is an array")
    comment: str | None = Field(default=None, description="Field comment")

    @field_validator("name")
    @classmethod
    def name_not_reserved(cls, v: str) -> str:
        """Validate that field name is not reserved"""
        reserved = ["id", "tenant_id", "project_id", "owner_user_id", "created_at", "updated_at"]
        if v in reserved:
            raise ValueError(f"Field name '{v}' is reserved")
        return v


class EntityOwnership(BaseModel):
    """Entity ownership configuration"""

    mode: OwnershipMode = Field(..., description="Ownership mode")
    field: str | None = Field(default="owner_user_id", description="Custom owner field name")


class EntityDefinition(BaseModel):
    """Entity (table) definition"""

    name: str = Field(..., pattern=r"^[A-Z][a-zA-Z0-9_]*$", description="Entity name")
    fields: list[FieldDefinition] = Field(..., min_length=1, description="Entity fields")
    ownership: EntityOwnership = Field(..., description="Entity ownership")
    indexes: list[str] | None = Field(default=None, description="Indexed field names")
    comment: str | None = Field(default=None, description="Entity comment")


class EntityPermissions(BaseModel):
    """Permissions for an entity"""

    read: PermissionType | None = Field(default=None, description="Read permission")
    write: PermissionType | None = Field(default=None, description="Write permission")
    delete: PermissionType | None = Field(default=None, description="Delete permission")


class DSLMetadata(BaseModel):
    """DSL metadata"""

    created_at: str | None = Field(default=None, description="Creation timestamp")
    updated_at: str | None = Field(default=None, description="Update timestamp")
    description: str | None = Field(default=None, description="Schema description")
    author: str | None = Field(default=None, description="Schema author")


class DSLSchema(BaseModel):
    """Complete DSL schema definition"""

    project_id: str = Field(..., description="Project UUID")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Schema version")
    tenant_mode: TenantMode = Field(default=TenantMode.ROW_ISOLATION, description="Tenant isolation mode")
    entities: dict[str, EntityDefinition] = Field(default_factory=dict, description="Entity definitions")
    permissions: dict[str, EntityPermissions] = Field(default_factory=dict, description="Entity permissions")
    metadata: DSLMetadata | None = Field(default=None, description="Schema metadata")


class SafetyCheckResult(BaseModel):
    """Safety check result"""

    is_safe: bool = Field(..., description="Whether schema is safe")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    blocked_operations: list[str] = Field(default_factory=list, description="Blocked operations")


class SchemaDiff(BaseModel):
    """Schema diff result"""

    added_entities: list[str] = Field(default_factory=list, description="Added entity names")
    removed_entities: list[str] = Field(default_factory=list, description="Removed entity names")
    modified_entities: dict[str, dict] = Field(default_factory=dict, description="Modified entities")
    permission_changes: dict[str, Any] = Field(default_factory=dict, description="Permission changes")


class Migration(BaseModel):
    """Migration record"""

    id: str = Field(..., description="Migration UUID")
    project_id: str = Field(..., description="Project UUID")
    version: str = Field(..., description="Schema version")
    type: Literal["create", "update", "rollback"] = Field(..., description="Migration type")
    sql_up: str = Field(..., description="Up migration SQL")
    sql_down: str = Field(..., description="Down migration SQL")
    hasura_metadata: dict[str, Any] = Field(..., description="Hasura metadata")
    status: Literal["pending", "applied", "failed", "rolled_back"] = Field(..., description="Migration status")
    created_at: str = Field(..., description="Creation timestamp")
    applied_at: str | None = Field(default=None, description="Application timestamp")
