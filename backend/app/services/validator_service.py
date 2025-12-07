"""
Validator Service

Validates mapping results against schema requirements.
Checks required fields, enum values, and data types.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re


class ValidationError:
    """Represents a single validation error."""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "message": self.message,
            "value": self.value,
        }


class ValidationResult:
    """Result of validation containing status and errors."""

    def __init__(self, valid: bool, errors: List[ValidationError]):
        self.valid = valid
        self.errors = errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
        }


def validate_type(value: Any, expected_type: str) -> bool:
    """
    Validate a value matches the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type string (string, int, float, date, boolean)

    Returns:
        True if type matches
    """
    if value is None:
        return True  # Null is valid for any type (required check is separate)

    if expected_type == "string":
        return isinstance(value, str)

    elif expected_type == "int":
        if isinstance(value, int) and not isinstance(value, bool):
            return True
        if isinstance(value, str):
            try:
                int(value)
                return True
            except ValueError:
                return False
        return False

    elif expected_type == "float":
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    elif expected_type == "date":
        if isinstance(value, datetime):
            return True
        if isinstance(value, str):
            # Try common date formats
            date_patterns = [
                r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
                r"^\d{2}/\d{2}/\d{4}$",  # MM/DD/YYYY
                r"^\d{2}-\d{2}-\d{4}$",  # DD-MM-YYYY
            ]
            return any(re.match(p, value) for p in date_patterns)
        return False

    elif expected_type == "boolean":
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ("true", "false", "yes", "no", "1", "0")
        return False

    elif expected_type == "enum":
        # Enum validation is handled separately
        return True

    return True  # Unknown types pass


def validate_enum(value: Any, enum_values: List[str]) -> bool:
    """
    Validate a value is in the enum list.

    Args:
        value: Value to validate
        enum_values: List of valid values

    Returns:
        True if value is in enum (case-insensitive)
    """
    if value is None:
        return True  # Null is valid (required check is separate)

    value_str = str(value).strip().lower()
    enum_lower = [e.lower() for e in enum_values]

    return value_str in enum_lower


def validate_mapping(
    mapping: Dict[str, Dict[str, Any]],
    schema: Dict[str, Any],
) -> ValidationResult:
    """
    Validate a complete mapping against a schema.

    Args:
        mapping: Mapping results {field: {value, source, confidence}}
        schema: Template schema with columns definition

    Returns:
        ValidationResult with status and errors
    """
    errors: List[ValidationError] = []
    columns = schema.get("columns", [])

    # Build lookup for schema columns
    column_lookup = {col["canonical"]: col for col in columns}

    # Check each required field
    for col in columns:
        canonical = col["canonical"]
        is_required = col.get("required", False)
        field_type = col.get("type", "string")
        enum_values = col.get("enum")

        field_mapping = mapping.get(canonical, {})
        value = field_mapping.get("value")

        # Required field check
        if is_required and (value is None or value == ""):
            errors.append(ValidationError(
                field=canonical,
                message=f"Required field '{canonical}' is missing or empty",
                value=value,
            ))
            continue

        # Skip further validation if no value
        if value is None:
            continue

        # Type validation
        if not validate_type(value, field_type):
            errors.append(ValidationError(
                field=canonical,
                message=f"Field '{canonical}' has invalid type. Expected {field_type}, got {type(value).__name__}",
                value=value,
            ))

        # Enum validation
        if enum_values and not validate_enum(value, enum_values):
            errors.append(ValidationError(
                field=canonical,
                message=f"Field '{canonical}' value '{value}' is not in allowed values: {enum_values}",
                value=value,
            ))

    # Check for extra fields not in schema (warning, not error)
    # for field in mapping:
    #     if field not in column_lookup:
    #         errors.append(ValidationError(
    #             field=field,
    #             message=f"Field '{field}' is not in the schema",
    #             value=mapping[field].get("value"),
    #         ))

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )


def validate_for_export(
    mapping: Dict[str, Dict[str, Any]],
    schema: Dict[str, Any],
    confidence_threshold: float = 0.5,
) -> ValidationResult:
    """
    Validate a mapping is ready for export to template.

    Includes confidence checks in addition to standard validation.

    Args:
        mapping: Mapping results
        schema: Template schema
        confidence_threshold: Minimum confidence for export

    Returns:
        ValidationResult with status and errors
    """
    # First run standard validation
    result = validate_mapping(mapping, schema)
    errors = list(result.errors)

    # Check confidence levels for required fields
    columns = schema.get("columns", [])

    for col in columns:
        if not col.get("required", False):
            continue

        canonical = col["canonical"]
        field_mapping = mapping.get(canonical, {})
        confidence = field_mapping.get("confidence", 0.0)

        if confidence < confidence_threshold:
            errors.append(ValidationError(
                field=canonical,
                message=f"Required field '{canonical}' has low confidence ({confidence:.2f} < {confidence_threshold})",
                value=field_mapping.get("value"),
            ))

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )


def get_validation_report(
    mapping: Dict[str, Dict[str, Any]],
    schema: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate a detailed validation report.

    Args:
        mapping: Mapping results
        schema: Template schema

    Returns:
        Detailed validation report
    """
    validation = validate_mapping(mapping, schema)
    columns = schema.get("columns", [])

    # Calculate statistics
    total_fields = len(columns)
    required_fields = sum(1 for c in columns if c.get("required", False))
    mapped_fields = sum(
        1 for c in columns
        if mapping.get(c["canonical"], {}).get("value") is not None
    )
    required_mapped = sum(
        1 for c in columns
        if c.get("required", False) and mapping.get(c["canonical"], {}).get("value") is not None
    )

    # Calculate average confidence
    confidences = [
        mapping.get(c["canonical"], {}).get("confidence", 0.0)
        for c in columns
        if mapping.get(c["canonical"], {}).get("value") is not None
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        "valid": validation.valid,
        "error_count": len(validation.errors),
        "errors": [e.to_dict() for e in validation.errors],
        "statistics": {
            "total_fields": total_fields,
            "required_fields": required_fields,
            "mapped_fields": mapped_fields,
            "required_mapped": required_mapped,
            "mapping_percentage": (mapped_fields / total_fields * 100) if total_fields > 0 else 0,
            "required_mapping_percentage": (required_mapped / required_fields * 100) if required_fields > 0 else 0,
            "average_confidence": avg_confidence,
        },
    }
