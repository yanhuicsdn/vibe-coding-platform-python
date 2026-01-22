"""
DSL Validator - Validate DSL schemas and perform safety checks
"""

from typing import Any

from vibe_coding.core.exceptions import SafetyException
from vibe_coding.models.dsl import (
    DSLSchema,
    EntityDefinition,
    FieldDefinition,
    SafetyCheckResult,
    SchemaDiff,
)


class DSLValidator:
    """Validator for DSL schemas"""

    @staticmethod
    def validate(schema: dict | DSLSchema) -> SafetyCheckResult:
        """
        Validate a DSL schema

        Args:
            schema: Schema to validate (dict or DSLSchema)

        Returns:
            SafetyCheckResult with validation status
        """
        errors = []
        warnings = []

        try:
            # If dict, convert to DSLSchema (Pydantic will validate)
            if isinstance(schema, dict):
                schema = DSLSchema(**schema)

            # Additional validation rules
            for entity_name, entity in schema.entities.items():
                # Check field count
                if len(entity.fields) > 50:
                    errors.append(
                        f"Entity '{entity_name}' has {len(entity.fields)} fields, "
                        f"exceeding limit of 50"
                    )

                # Check for reserved field names
                reserved_fields = [
                    "id",
                    "tenant_id",
                    "project_id",
                    "owner_user_id",
                    "created_at",
                    "updated_at",
                ]
                for field in entity.fields:
                    if field.name in reserved_fields:
                        errors.append(
                            f"Entity '{entity_name}' contains reserved field '{field.name}'"
                        )

            # Check entity count
            if len(schema.entities) > 100:
                errors.append(
                    f"Schema has {len(schema.entities)} entities, exceeding limit of 100"
                )

            # Permission safety checks
            for entity_name, perms in schema.permissions.items():
                entity = schema.entities.get(entity_name)
                if not entity:
                    continue

                # Check for overly permissive settings
                if perms.read == "public" or perms.write == "public":
                    warnings.append(
                        f"Entity '{entity_name}' has public permissions - "
                        "ensure this is intentional"
                    )

                # Owner-based entities should have owner permissions
                if entity.ownership.mode == "user":
                    if perms.read != "owner" or perms.write != "owner":
                        warnings.append(
                            f"Entity '{entity_name}' is user-owned but has non-owner permissions"
                        )

            return SafetyCheckResult(
                is_safe=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                blocked_operations=[],
            )

        except Exception as e:
            return SafetyCheckResult(
                is_safe=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=warnings,
                blocked_operations=[],
            )

    @staticmethod
    async def safety_check(
        new_schema: DSLSchema,
        old_schema: DSLSchema | None = None,
        max_fields_per_entity: int = 50,
        max_entities_per_project: int = 100,
    ) -> SafetyCheckResult:
        """
        Perform safety checks on schema changes

        Args:
            new_schema: New schema to check
            old_schema: Previous schema (for diff checks)
            max_fields_per_entity: Maximum fields per entity
            max_entities_per_project: Maximum entities per project

        Returns:
            SafetyCheckResult with safety status
        """
        errors = []
        warnings = []
        blocked_operations = []

        # Check 1: Entity count limit
        entity_count = len(new_schema.entities)
        if entity_count > max_entities_per_project:
            errors.append(
                f"Entity count ({entity_count}) exceeds maximum allowed ({max_entities_per_project})"
            )

        # Check 2: Field count per entity
        for entity_name, entity in new_schema.entities.items():
            if len(entity.fields) > max_fields_per_entity:
                errors.append(
                    f"Entity '{entity_name}' has {len(entity.fields)} fields, "
                    f"exceeding limit of {max_fields_per_entity}"
                )

        # Check 3: Reserved field names (cannot be modified by AI)
        reserved_fields = ["tenant_id", "project_id", "owner_user_id"]
        for entity_name, entity in new_schema.entities.items():
            for field in entity.fields:
                if field.name in reserved_fields:
                    blocked_operations.append(
                        f"Entity '{entity_name}' contains reserved field '{field.name}'"
                    )

        # Check 4: Dangerous field removals (if old schema exists)
        if old_schema:
            for entity_name, old_entity in old_schema.entities.items():
                new_entity = new_schema.entities.get(entity_name)

                if not new_entity:
                    warnings.append(f"Entity '{entity_name}' will be deleted")
                    continue

                old_field_names = {f.name for f in old_entity.fields}
                new_field_names = {f.name for f in new_entity.fields}

                for field_name in old_field_names:
                    if field_name not in new_field_names:
                        if field_name in reserved_fields:
                            errors.append(
                                f"Cannot remove reserved field '{field_name}' from '{entity_name}'"
                            )
                        else:
                            warnings.append(f"Field '{field_name}' will be removed from '{entity_name}'")

        # Check 5: Type compatibility checks
        if old_schema:
            for entity_name, old_entity in old_schema.entities.items():
                new_entity = new_schema.entities.get(entity_name)
                if not new_entity:
                    continue

                old_fields_map = {f.name: f for f in old_entity.fields}
                new_fields_map = {f.name: f for f in new_entity.fields}

                for field_name, new_field in new_fields_map.items():
                    old_field = old_fields_map.get(field_name)
                    if old_field and old_field.type != new_field.type:
                        errors.append(
                            f"Cannot change type of field '{field_name}' in '{entity_name}' "
                            f"from {old_field.type} to {new_field.type}"
                        )

        # Check 6: Permission safety
        for entity_name, perms in new_schema.permissions.items():
            entity = new_schema.entities.get(entity_name)
            if not entity:
                continue

            # Check for overly permissive settings
            if perms.read == "public" or perms.write == "public":
                warnings.append(
                    f"Entity '{entity_name}' has public permissions - ensure this is intentional"
                )

            # Owner-based entities should have owner permissions
            if entity.ownership.mode == "user":
                if perms.read != "owner" or perms.write != "owner":
                    warnings.append(
                        f"Entity '{entity_name}' is user-owned but has non-owner permissions"
                    )

        is_safe = len(errors) == 0 and len(blocked_operations) == 0

        return SafetyCheckResult(
            is_safe=is_safe,
            errors=errors,
            warnings=warnings,
            blocked_operations=blocked_operations,
        )
