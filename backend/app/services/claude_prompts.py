"""
Claude AI Prompt Templates

Contains the structured prompts used for AI-assisted attribute extraction.
"""
import json
from typing import Any, Dict, List


# The main extraction prompt template
EXTRACTION_PROMPT = """You are a structured extraction model. Your task is to extract product attributes and map them to canonical schema fields.

## Inputs

### 1. Canonical Schema
The following JSON array defines the canonical fields you must map to. Each field has:
- `canonical`: The field name to use in your output
- `type`: Expected data type (string, int, float, date, enum)
- `enum`: If present, the value MUST be one of these options (case-insensitive match allowed)
- `required`: Whether the field is required

```json
{canonical_schema}
```

### 2. Normalized Product Data
The following JSON contains the product information to extract from:

```json
{normalized_product}
```

## Task

Map each canonical field from the schema to a value extracted from the product data.

Return a JSON object where each key is a canonical field name, and the value is an object with:
- `value`: The extracted value (string, number, or null if not found)
- `source`: Where you found it - one of: "title", "description", "metafield", "variant", "ai_inferred"
- `confidence`: A float from 0.00 to 1.00 indicating your confidence in the extraction

## Rules

1. **ONLY** return keys that exist in the canonical_schema. Do NOT create new keys.
2. Values must be single scalar values (string, number, boolean) or null. No arrays or objects.
3. For `enum` fields, the value MUST match one of the enum options (case-insensitive). If no match, return null.
4. If you cannot find or infer a value, set `value` to null, `source` to "not_found", and `confidence` to 0.0.
5. Return ONLY the JSON object. No explanations, no markdown formatting, no additional text.

## Confidence Guidelines

- 0.90-1.00: Direct exact match found in data
- 0.75-0.89: Strong inference from context (e.g., "100% cotton" → fabric: "Cotton")
- 0.50-0.74: Moderate inference or partial match
- 0.25-0.49: Weak inference, educated guess
- 0.00-0.24: Very uncertain or not found

## Example

Input schema field: {{"canonical": "fabric", "type": "string", "enum": ["Cotton", "Silk", "Polyester"]}}
Input product: {{"cleaned_description": "Made from 100% organic cotton fabric"}}

Output for this field:
{{"fabric": {{"value": "Cotton", "source": "description", "confidence": 0.90}}}}

Now extract all fields from the provided product data."""


def build_extraction_prompt(
    canonical_schema: List[Dict[str, Any]],
    normalized_product: Dict[str, Any],
) -> str:
    """
    Build the complete extraction prompt for Claude.

    Args:
        canonical_schema: List of column definitions from template schema
        normalized_product: Normalized product data

    Returns:
        Complete prompt string
    """
    # Simplify schema for prompt (only include relevant fields)
    simplified_schema = [
        {
            "canonical": col["canonical"],
            "type": col.get("type", "string"),
            "enum": col.get("enum"),
            "required": col.get("required", False),
        }
        for col in canonical_schema
    ]

    # Simplify product data to reduce token usage
    simplified_product = {
        "cleaned_title": normalized_product.get("cleaned_title", ""),
        "cleaned_description": normalized_product.get("cleaned_description", ""),
        "vendor": normalized_product.get("vendor", ""),
        "product_type": normalized_product.get("product_type", ""),
        "tags": normalized_product.get("tags", []),
        "metafields": normalized_product.get("metafields", {}),
        "variants_simplified": normalized_product.get("variants_simplified", [])[:3],  # Limit variants
        "extracted_materials": normalized_product.get("extracted_materials", []),
        "extracted_colors": normalized_product.get("extracted_colors", []),
        "sizes": normalized_product.get("sizes", []),
    }

    return EXTRACTION_PROMPT.format(
        canonical_schema=json.dumps(simplified_schema, indent=2),
        normalized_product=json.dumps(simplified_product, indent=2),
    )


def build_focused_extraction_prompt(
    fields_to_extract: List[str],
    canonical_schema: List[Dict[str, Any]],
    normalized_product: Dict[str, Any],
) -> str:
    """
    Build a focused extraction prompt for specific missing fields.

    Args:
        fields_to_extract: List of canonical field names to extract
        canonical_schema: Full schema columns
        normalized_product: Normalized product data

    Returns:
        Complete prompt string focused on specific fields
    """
    # Filter schema to only requested fields
    filtered_schema = [
        col for col in canonical_schema
        if col["canonical"] in fields_to_extract
    ]

    return build_extraction_prompt(filtered_schema, normalized_product)


# Validation prompt for checking AI responses
VALIDATION_PROMPT = """You are a validation model. Check if the following mapping is correct.

Product Title: {title}
Product Description: {description}

Proposed Mapping:
Field: {field}
Value: {value}
Source: {source}

Question: Is this mapping accurate based on the product information?

Respond with only one word: "correct" or "incorrect"
"""


def build_validation_prompt(
    product: Dict[str, Any],
    field: str,
    value: Any,
    source: str,
) -> str:
    """
    Build a validation prompt to verify a mapping.

    Args:
        product: Product data
        field: Field name being validated
        value: Proposed value
        source: Where the value came from

    Returns:
        Validation prompt string
    """
    return VALIDATION_PROMPT.format(
        title=product.get("cleaned_title", product.get("title", "")),
        description=product.get("cleaned_description", product.get("description", ""))[:500],
        field=field,
        value=value,
        source=source,
    )


# System message for Claude API calls
SYSTEM_MESSAGE = """You are a precise data extraction assistant for e-commerce product mapping.
Your responses must be valid JSON only, with no additional text or explanation.
You excel at:
- Extracting structured data from unstructured product descriptions
- Matching values to predefined enum options
- Inferring missing attributes from context
- Providing accurate confidence scores

Always prioritize accuracy over completeness. If uncertain, return null with low confidence rather than guessing."""


def get_system_message() -> str:
    """Get the system message for Claude API calls."""
    return SYSTEM_MESSAGE
