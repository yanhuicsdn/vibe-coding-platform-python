"""
DSL Diff Engine - Compute differences between schema versions
"""

from vibe_coding.models.dsl import DSLSchema, EntityDefinition, FieldDefinition, SchemaDiff


class DSLDiff:
    """Compute differences between DSL schemas"""

    @staticmethod
    def compute(old_schema: DSLSchema, new_schema: DSLSchema) -> SchemaDiff:
        """
        Compute differences between two schemas

        Args:
            old_schema: Previous schema
            new_schema: New schema

        Returns:
            SchemaDiff with all changes
        """
        added_entities = []
        removed_entities = []
        modified_entities = {}
        permission_changes = {}

        # Check for added and removed entities
        old_entity_names = set(old_schema.entities.keys())
        new_entity_names = set(new_schema.entities.keys())

        added_entities = list(new_entity_names - old_entity_names)
        removed_entities = list(old_entity_names - new_entity_names)

        # Check for modified entities
        for name in new_entity_names & old_entity_names:
            old_entity = old_schema.entities[name]
            new_entity = new_schema.entities[name]

            entity_diff = DSLDiff._compute_entity_diff(old_entity, new_entity)
            if (
                entity_diff["added_fields"]
                or entity_diff["removed_fields"]
                or entity_diff["modified_fields"]
            ):
                modified_entities[name] = entity_diff

        # Check for permission changes
        old_permissions = old_schema.permissions
        new_permissions = new_schema.permissions

        for entity, perms in new_permissions.items():
            if entity not in old_permissions:
                permission_changes[entity] = {"type": "added", "permissions": perms.model_dump()}
            elif old_permissions[entity].model_dump() != perms.model_dump():
                permission_changes[entity] = {
                    "type": "modified",
                    "old": old_permissions[entity].model_dump(),
                    "new": perms.model_dump(),
                }

        for entity in old_permissions:
            if entity not in new_permissions:
                permission_changes[entity] = {"type": "removed"}

        return SchemaDiff(
            added_entities=added_entities,
            removed_entities=removed_entities,
            modified_entities=modified_entities,
            permission_changes=permission_changes,
        )

    @staticmethod
    def _compute_entity_diff(
        old_entity: EntityDefinition, new_entity: EntityDefinition
    ) -> dict:
        """
        Compute diff for a single entity

        Args:
            old_entity: Previous entity
            new_entity: New entity

        Returns:
            Dictionary with added/removed/modified fields
        """
        added_fields = []
        removed_fields = []
        modified_fields = {}

        old_fields = {f.name: f for f in old_entity.fields}
        new_fields = {f.name: f for f in new_entity.fields}

        old_field_names = set(old_fields.keys())
        new_field_names = set(new_fields.keys())

        added_fields = list(new_field_names - old_field_names)
        removed_fields = list(old_field_names - new_field_names)

        for name in new_field_names & old_field_names:
            old_field = old_fields[name]
            new_field = new_fields[name]

            if not DSLDiff._fields_equal(old_field, new_field):
                modified_fields[name] = {
                    "old": old_field.model_dump(),
                    "new": new_field.model_dump(),
                }

        return {
            "added_fields": added_fields,
            "removed_fields": removed_fields,
            "modified_fields": modified_fields,
        }

    @staticmethod
    def _fields_equal(a: FieldDefinition, b: FieldDefinition) -> bool:
        """
        Check if two fields are equal

        Args:
            a: First field
            b: Second field

        Returns:
            True if fields are equal
        """
        return (
            a.name == b.name
            and a.type == b.type
            and a.required == b.required
            and a.unique == b.unique
            and a.nullable == b.nullable
            and a.array == b.array
            and a.default_value == b.default_value
        )

    @staticmethod
    def is_backward_compatible(diff: SchemaDiff) -> bool:
        """
        Check if a diff is backward compatible

        Args:
            diff: Schema diff to check

        Returns:
            True if backward compatible
        """
        # Removing entities is not backward compatible
        if diff.removed_entities:
            return False

        # Removing fields is not backward compatible
        for entity_diff in diff.modified_entities.values():
            if entity_diff["removed_fields"]:
                return False

            # Type changes are not backward compatible
            for field, change in entity_diff["modified_fields"].items():
                if change["old"]["type"] != change["new"]["type"]:
                    return False

                # Making a field required is not backward compatible
                if not change["old"]["required"] and change["new"]["required"]:
                    return False

        # Restrictive permission changes might break existing code
        for perm_change in diff.permission_changes.values():
            if perm_change["type"] == "removed":
                return False

        return True

    @staticmethod
    def summarize(diff: SchemaDiff) -> str:
        """
        Generate a human-readable diff summary

        Args:
            diff: Schema diff to summarize

        Returns:
            Summary string
        """
        lines = []

        if diff.added_entities:
            lines.append(f"Added entities: {', '.join(diff.added_entities)}")

        if diff.removed_entities:
            lines.append(f"Removed entities: {', '.join(diff.removed_entities)}")

        for entity, entity_diff in diff.modified_entities.items():
            if entity_diff["added_fields"]:
                lines.append(f"{entity}: added fields {', '.join(entity_diff['added_fields'])}")
            if entity_diff["removed_fields"]:
                lines.append(f"{entity}: removed fields {', '.join(entity_diff['removed_fields'])}")
            if entity_diff["modified_fields"]:
                lines.append(f"{entity}: modified fields {', '.join(entity_diff['modified_fields'].keys())}")

        for entity, perm_change in diff.permission_changes.items():
            lines.append(f"{entity}: permissions {perm_change['type']}")

        return "\n".join(lines) if lines else "No changes"
