"""
SQL Generator - Generate SQL migrations from DSL schemas
"""

from vibe_coding.models.dsl import DSLSchema, EntityDefinition, FieldDefinition, TenantMode


class SQLGenerator:
    """Generate SQL migrations from DSL schemas"""

    @staticmethod
    def generate_create_table(entity: EntityDefinition, tenant_mode: TenantMode) -> str:
        """
        Generate SQL for creating a table from an entity

        Args:
            entity: Entity definition
            tenant_mode: Tenant isolation mode

        Returns:
            SQL CREATE TABLE statement
        """
        table_name = SQLGenerator._table_name(entity.name)
        lines = []

        lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")

        # Primary key
        id_field = next((f for f in entity.fields if f.name == "id"), None)
        if id_field:
            lines.append(f"  id {SQLGenerator._map_type(id_field)} PRIMARY KEY DEFAULT gen_random_uuid(),")
        else:
            lines.append("  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),")

        # Multi-tenant required fields
        if tenant_mode == TenantMode.ROW_ISOLATION:
            lines.append("  tenant_id uuid NOT NULL,")
            lines.append("  project_id uuid NOT NULL,")
            lines.append("  owner_user_id uuid,")

        # Entity fields
        for field in entity.fields:
            if field.name == "id":
                continue  # Already added

            column_def = SQLGenerator._generate_column_def(field)
            lines.append(f"  {column_def},")

        # Timestamps
        lines.append("  created_at timestamptz DEFAULT now(),")
        lines.append("  updated_at timestamptz DEFAULT now(),")

        # Remove trailing comma
        lines[-1] = lines[-1].rstrip(",")

        lines.append(");")

        # Add indexes
        if tenant_mode == TenantMode.ROW_ISOLATION:
            lines.append("")
            lines.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_tenant ON {table_name}(tenant_id);")
            lines.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_project ON {table_name}(project_id);")
            lines.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_owner ON {table_name}(owner_user_id);")

        # Custom indexes
        if entity.indexes:
            for index in entity.indexes:
                lines.append("")
                lines.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{index} ON {table_name}({index});")

        return "\n".join(lines)

    @staticmethod
    def generate_drop_table(entity_name: str) -> str:
        """
        Generate SQL for dropping a table

        Args:
            entity_name: Entity name

        Returns:
            SQL DROP TABLE statement
        """
        table_name = SQLGenerator._table_name(entity_name)
        return f"DROP TABLE IF NOT EXISTS {table_name} CASCADE;"

    @staticmethod
    def generate_add_column(entity_name: str, field: FieldDefinition) -> str:
        """
        Generate SQL for adding a column

        Args:
            entity_name: Entity name
            field: Field definition

        Returns:
            SQL ALTER TABLE statement
        """
        table_name = SQLGenerator._table_name(entity_name)
        column_def = SQLGenerator._generate_column_def(field)
        return f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_def};"

    @staticmethod
    def generate_drop_column(entity_name: str, field_name: str) -> str:
        """
        Generate SQL for dropping a column

        Args:
            entity_name: Entity name
            field_name: Field name

        Returns:
            SQL ALTER TABLE statement
        """
        table_name = SQLGenerator._table_name(entity_name)
        return f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {field_name};"

    @staticmethod
    def generate_migration(old_schema: DSLSchema | None, new_schema: DSLSchema) -> dict[str, str]:
        """
        Generate complete migration SQL

        Args:
            old_schema: Previous schema (None for initial migration)
            new_schema: New schema to apply

        Returns:
            Dictionary with 'up' and 'down' SQL
        """
        up_statements = []
        down_statements = []

        # If no old schema, create all tables
        if not old_schema:
            for entity in new_schema.entities.values():
                up_statements.append(SQLGenerator.generate_create_table(entity, new_schema.tenant_mode))
                down_statements.append(SQLGenerator.generate_drop_table(entity.name))
        else:
            # TODO: Implement incremental migration generation
            # This would involve comparing old and new schemas
            pass

        return {
            "up": "\n\n".join(up_statements),
            "down": "\n\n".join(down_statements),
        }

    @staticmethod
    def _generate_column_def(field: FieldDefinition) -> str:
        """Generate column definition SQL"""
        column_def = f"{field.name} {SQLGenerator._map_type(field)}"

        if field.array:
            column_def += "[]"

        if not field.nullable:
            column_def += " NOT NULL"

        if field.unique:
            column_def += " UNIQUE"

        if field.default_value is not None:
            column_def += f" DEFAULT {SQLGenerator._format_default_value(field.default_value, field.type)}"

        return column_def

    @staticmethod
    def _map_type(field: FieldDefinition) -> str:
        """Map DSL type to PostgreSQL type"""
        type_map = {
            "string": "varchar(255)",
            "text": "text",
            "integer": "integer",
            "float": "numeric",
            "boolean": "boolean",
            "date": "date",
            "timestamp": "timestamptz",
            "uuid": "uuid",
            "json": "jsonb",
            "array": "jsonb",
        }

        return type_map.get(field.type, "text")

    @staticmethod
    def _format_default_value(value: any, field_type: str) -> str:
        """Format default value for SQL"""
        if value is None:
            return "NULL"

        match field_type:
            case "string" | "text" | "date" | "timestamp":
                return f"'{value}'"
            case "boolean":
                return "TRUE" if value else "FALSE"
            case "json" | "array":
                import json

                return f"'{json.dumps(value)}'::jsonb"
            case _:
                return str(value)

    @staticmethod
    def _table_name(entity_name: str) -> str:
        """Convert entity name to table name"""
        # PascalCase to snake_case with prefix
        import re

        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", entity_name).lower()
        return f"project_{snake}"
