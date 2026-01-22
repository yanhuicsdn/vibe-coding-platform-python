"""
DSL Parser - Parse DSL from YAML and JSON formats
"""

import yaml
from vibe_coding.core.exceptions import ValidationException
from vibe_coding.models.dsl import DSLSchema


class DSLParser:
    """Parser for DSL schemas"""

    @staticmethod
    def from_yaml(yaml_string: str) -> DSLSchema:
        """
        Parse DSL from YAML string

        Args:
            yaml_string: YAML string containing DSL schema

        Returns:
            Parsed DSLSchema

        Raises:
            ValidationException: If parsing or validation fails
        """
        try:
            data = yaml.safe_load(yaml_string)
            return DSLSchema(**data)
        except yaml.YAMLError as e:
            raise ValidationException(f"YAML parsing failed: {str(e)}")
        except Exception as e:
            raise ValidationException(f"Validation failed: {str(e)}")

    @staticmethod
    def from_json(json_string: str) -> DSLSchema:
        """
        Parse DSL from JSON string

        Args:
            json_string: JSON string containing DSL schema

        Returns:
            Parsed DSLSchema

        Raises:
            ValidationException: If parsing or validation fails
        """
        import json

        try:
            data = json.loads(json_string)
            return DSLSchema(**data)
        except json.JSONDecodeError as e:
            raise ValidationException(f"JSON parsing failed: {str(e)}")
        except Exception as e:
            raise ValidationException(f"Validation failed: {str(e)}")

    @staticmethod
    def from_dict(data: dict) -> DSLSchema:
        """
        Parse DSL from dictionary

        Args:
            data: Dictionary containing DSL schema

        Returns:
            Parsed DSLSchema

        Raises:
            ValidationException: If validation fails
        """
        try:
            return DSLSchema(**data)
        except Exception as e:
            raise ValidationException(f"Validation failed: {str(e)}")

    @staticmethod
    def to_yaml(schema: DSLSchema) -> str:
        """
        Convert DSL schema to YAML string

        Args:
            schema: DSLSchema to convert

        Returns:
            YAML string
        """
        return yaml.dump(schema.model_dump(exclude_none=True), sort_keys=False)

    @staticmethod
    def to_json(schema: DSLSchema, indent: int = 2) -> str:
        """
        Convert DSL schema to JSON string

        Args:
            schema: DSLSchema to convert
            indent: JSON indentation

        Returns:
            JSON string
        """
        import json

        return json.dumps(schema.model_dump(exclude_none=True), indent=indent)

    @staticmethod
    def create_minimal_schema(project_id: str) -> DSLSchema:
        """
        Create a minimal valid DSL schema

        Args:
            project_id: Project UUID

        Returns:
            Minimal DSLSchema
        """
        from datetime import datetime

        return DSLSchema(
            project_id=project_id,
            version="1.0.0",
            tenant_mode="row_isolation",
            entities={},
            permissions={},
            metadata={
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
