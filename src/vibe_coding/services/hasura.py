"""
Hasura Metadata API and GraphQL Client
"""

import httpx
from typing import Any

from vibe_coding.core.exceptions import HasuraException
from vibe_coding.models.dsl import EntityDefinition, EntityPermissions
from vibe_coding.models.schema import HasuraPermissionFilter, HasuraTablePermission


class HasuraMetadataClient:
    """Client for Hasura Metadata API"""

    def __init__(self, graphql_url: str, admin_secret: str):
        """
        Initialize Hasura Metadata client

        Args:
            graphql_url: Hasura GraphQL URL
            admin_secret: Hasura admin secret
        """
        self.graphql_url = graphql_url
        self.admin_secret = admin_secret
        self.metadata_url = f"{graphql_url}/v1/metadata"
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"x-hasura-admin-secret": self.admin_secret},
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def execute_metadata(self, type_: str, args: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a metadata API call

        Args:
            type_: Metadata operation type
            args: Operation arguments

        Returns:
            Response data

        Raises:
            HasuraException: If operation fails
        """
        client = await self._get_client()

        payload = {"type": type_, "args": args, "version": 2}

        response = await client.post(self.metadata_url, json=payload)
        result = response.json()

        if response.status_code != 200 or result.get("error"):
            raise HasuraException(
                f"Hasura metadata operation failed: {result.get('error') or result.get('message', 'Unknown error')}"
            )

        return result

    async def create_table(self, entity: EntityDefinition) -> None:
        """
        Create a table in Hasura

        Args:
            entity: Entity definition
        """
        table_name = self._to_snake_case(entity.name)

        columns = [
            {"name": "id", "type": "uuid", "nullable": False, "unique": True},
            {"name": "tenant_id", "type": "uuid", "nullable": False},
            {"name": "project_id", "type": "uuid", "nullable": False},
            {"name": "owner_user_id", "type": "uuid", "nullable": True},
            {"name": "created_at", "type": "timestamptz", "nullable": True},
            {"name": "updated_at", "type": "timestamptz", "nullable": True},
        ]

        for field in entity.fields:
            if field.name in ["id", "tenant_id", "project_id", "owner_user_id", "created_at", "updated_at"]:
                continue

            columns.append(
                {
                    "name": field.name,
                    "type": self._map_type(field.type),
                    "nullable": field.nullable if field.nullable is not None else True,
                    "unique": field.unique if field.unique is not None else False,
                }
            )

        await self.execute_metadata(
            "pg_create_table",
            {
                "table": {"name": table_name, "schema": "public"},
                "columns": columns,
                "primary_key": {"column_names": ["id"]},
            },
        )

    async def track_table(self, table_name: str) -> None:
        """
        Track a table in Hasura

        Args:
            table_name: Table name
        """
        await self.execute_metadata(
            "track_table",
            {"table": {"name": self._to_snake_case(table_name), "schema": "public"}},
        )

    async def untrack_table(self, table_name: str) -> None:
        """
        Untrack a table in Hasura

        Args:
            table_name: Table name
        """
        await self.execute_metadata(
            "untrack_table",
            {"table": {"name": self._to_snake_case(table_name), "schema": "public"}},
        )

    async def create_select_permission(
        self, table_name: str, role: str, permission: HasuraTablePermission
    ) -> None:
        """
        Create select permission for a table

        Args:
            table_name: Table name
            role: Role name
            permission: Permission definition
        """
        args: dict[str, Any] = {
            "table": {"name": self._to_snake_case(table_name), "schema": "public"},
            "role": role,
            "permission": {
                "allow_aggregations": permission.allow_aggregations,
            },
        }

        if permission.filter:
            args["permission"]["filter"] = permission.filter

        if permission.columns:
            args["permission"]["columns"] = permission.columns
        else:
            args["permission"]["columns"] = "*"

        await self.execute_metadata("pg_create_select_permission", args)

    async def create_insert_permission(
        self, table_name: str, role: str, permission: HasuraTablePermission
    ) -> None:
        """
        Create insert permission for a table

        Args:
            table_name: Table name
            role: Role name
            permission: Permission definition
        """
        args: dict[str, Any] = {
            "table": {"name": self._to_snake_case(table_name), "schema": "public"},
            "role": role,
            "permission": {},
        }

        if permission.check:
            args["permission"]["check"] = permission.check

        if permission.set:
            args["permission"]["set"] = permission.set

        if permission.columns:
            args["permission"]["columns"] = permission.columns
        else:
            args["permission"]["columns"] = "*"

        await self.execute_metadata("pg_create_insert_permission", args)

    async def create_update_permission(
        self, table_name: str, role: str, permission: HasuraTablePermission
    ) -> None:
        """
        Create update permission for a table

        Args:
            table_name: Table name
            role: Role name
            permission: Permission definition
        """
        args: dict[str, Any] = {
            "table": {"name": self._to_snake_case(table_name), "schema": "public"},
            "role": role,
            "permission": {},
        }

        if permission.filter:
            args["permission"]["filter"] = permission.filter

        if permission.check:
            args["permission"]["check"] = permission.check

        if permission.set:
            args["permission"]["set"] = permission.set

        if permission.columns:
            args["permission"]["columns"] = permission.columns
        else:
            args["permission"]["columns"] = "*"

        await self.execute_metadata("pg_create_update_permission", args)

    async def create_delete_permission(
        self, table_name: str, role: str, permission: HasuraTablePermission
    ) -> None:
        """
        Create delete permission for a table

        Args:
            table_name: Table name
            role: Role name
            permission: Permission definition
        """
        args: dict[str, Any] = {
            "table": {"name": self._to_snake_case(table_name), "schema": "public"},
            "role": role,
            "permission": {},
        }

        if permission.filter:
            args["permission"]["filter"] = permission.filter

        await self.execute_metadata("pg_create_delete_permission", args)

    async def apply_entity_permissions(
        self, entity_name: str, permissions: EntityPermissions
    ) -> None:
        """
        Apply all permissions for an entity

        Args:
            entity_name: Entity name
            permissions: Permission configuration
        """
        roles = ["user", "admin"]

        # Owner-based permissions
        owner_filter = {
            "and": [
                {"tenant_id": {"_eq": "X-Hasura-Tenant-Id"}},
                {"project_id": {"_eq": "X-Hasura-Project-Id"}},
                {"owner_user_id": {"_eq": "X-Hasura-User-Id"}},
            ]
        }

        # Tenant-based permissions
        tenant_filter = {
            "and": [
                {"tenant_id": {"_eq": "X-Hasura-Tenant-Id"}},
                {"project_id": {"_eq": "X-Hasura-Project-Id"}},
            ]
        }

        for role in roles:
            select_filter = owner_filter if permissions.read == "owner" else tenant_filter

            if permissions.read:
                await self.create_select_permission(
                    entity_name,
                    role,
                    HasuraTablePermission(filter=select_filter, columns=None),
                )

            if permissions.write:
                check = owner_filter if permissions.write == "owner" else tenant_filter
                await self.create_insert_permission(
                    entity_name,
                    role,
                    HasuraTablePermission(
                        check=check,
                        set={
                            "owner_user_id": "X-Hasura-User-Id",
                            "tenant_id": "X-Hasura-Tenant-Id",
                            "project_id": "X-Hasura-Project-Id",
                        },
                        columns=None,
                    ),
                )

            if permissions.read:  # Update uses same filter as read
                await self.create_update_permission(
                    entity_name,
                    role,
                    HasuraTablePermission(
                        filter=select_filter,
                        check=select_filter,
                        columns=None,
                    ),
                )

            if permissions.delete:
                delete_filter = owner_filter if permissions.delete == "owner" else tenant_filter
                await self.create_delete_permission(
                    entity_name,
                    role,
                    HasuraTablePermission(filter=delete_filter),
                )

    async def reload_metadata(self) -> None:
        """Reload Hasura metadata"""
        await self.execute_metadata("reload_metadata", {})

    async def export_metadata(self) -> dict[str, Any]:
        """
        Export current Hasura metadata

        Returns:
            Metadata dictionary
        """
        client = await self._get_client()

        response = await client.post(
            self.metadata_url,
            json={"type": "export_metadata", "args": {}, "version": 2},
        )

        if response.status_code != 200:
            raise HasuraException(f"Failed to export metadata: {response.text}")

        return response.json()

    def _map_type(self, field_type: str) -> str:
        """Map DSL type to Hasura type"""
        type_map = {
            "string": "text",
            "text": "text",
            "integer": "integer",
            "float": "float",
            "boolean": "boolean",
            "date": "date",
            "timestamp": "timestamptz",
            "uuid": "uuid",
            "json": "jsonb",
            "array": "jsonb",
        }

        return type_map.get(field_type, "text")

    def _to_snake_case(self, str_: str) -> str:
        """Convert PascalCase to snake_case"""
        import re

        return re.sub(r"(?<!^)(?=[A-Z])", "_", str_).lower()


class GraphQLClient:
    """Client for Hasura GraphQL queries"""

    def __init__(self, graphql_url: str, admin_secret: str | None = None, jwt_token: str | None = None):
        """
        Initialize GraphQL client

        Args:
            graphql_url: Hasura GraphQL URL
            admin_secret: Admin secret (for admin operations)
            jwt_token: JWT token (for user operations)
        """
        self.graphql_url = f"{graphql_url}/v1/graphql"
        self.admin_secret = admin_secret
        self.jwt_token = jwt_token
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            headers = {"Content-Type": "application/json"}

            if self.admin_secret:
                headers["x-hasura-admin-secret"] = self.admin_secret
            elif self.jwt_token:
                headers["Authorization"] = f"Bearer {self.jwt_token}"

            self._client = httpx.AsyncClient(headers=headers, timeout=30.0)

        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def query(
        self, query: str, variables: dict[str, Any] | None = None, operation_name: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a GraphQL query

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name

        Returns:
            Query result data

        Raises:
            HasuraException: If query fails
        """
        client = await self._get_client()

        payload: dict[str, Any] = {"query": query}

        if variables:
            payload["variables"] = variables

        if operation_name:
            payload["operationName"] = operation_name

        response = await client.post(self.graphql_url, json=payload)
        result = response.json()

        if response.status_code != 200 or result.get("errors"):
            errors = result.get("errors", [])
            error_msg = ", ".join(e.get("message", str(e)) for e in errors)
            raise HasuraException(f"GraphQL query failed: {error_msg}")

        return result.get("data", {})

    async def mutate(
        self, mutation: str, variables: dict[str, Any] | None = None, operation_name: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a GraphQL mutation

        Args:
            mutation: GraphQL mutation string
            variables: Mutation variables
            operation_name: Operation name

        Returns:
            Mutation result data
        """
        return await self.query(mutation, variables, operation_name)
