#!/usr/bin/env python3
"""
Template Ingestion Tool

Reads marketplace Excel templates (.xlsx/.xlsm) and generates canonical JSON schemas.
This tool extracts column headers, detects types, and normalizes field names to
create a standardized schema for product mapping.

Usage:
    python -m app.tools.template_ingest <template_path> <marketplace> <category>

Example:
    python -m app.tools.template_ingest ./templates/amazon_shirt.xlsx amazon shirt
"""
import argparse
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


# Synonym mapping for canonical field names
SYNONYM_MAP: Dict[str, str] = {
    # SKU variations
    "sku": "sku",
    "item_sku": "sku",
    "product_sku": "sku",
    "seller_sku": "sku",
    "item_number": "sku",
    "product_id": "sku",
    "article_number": "sku",

    # Parent SKU variations
    "parent_sku": "parent_sku",
    "parent_child": "parent_sku",
    "parentage": "parent_sku",
    "parent_id": "parent_sku",
    "group_id": "parent_sku",

    # Title variations
    "title": "title",
    "product_title": "title",
    "item_title": "title",
    "product_name": "title",
    "item_name": "title",
    "name": "title",

    # Description variations
    "description": "description",
    "product_description": "description",
    "item_description": "description",
    "long_description": "description",
    "bullet_point": "bullet_points",
    "bullet_points": "bullet_points",
    "key_product_features": "bullet_points",

    # Price variations
    "price": "price",
    "standard_price": "price",
    "list_price": "price",
    "sale_price": "sale_price",
    "mrp": "mrp",
    "maximum_retail_price": "mrp",

    # Size variations
    "size": "size",
    "size_name": "size",
    "item_size": "size",
    "product_size": "size",
    "size_map": "size_map",

    # Color variations
    "color": "color",
    "color_name": "color",
    "colour": "color",
    "colour_name": "color",
    "color_map": "color_map",

    # Fabric/Material variations
    "fabric": "fabric",
    "fabric_type": "fabric",
    "material": "material",
    "material_type": "material",
    "fabric_composition": "fabric_composition",
    "material_composition": "material_composition",
    "outer_material": "outer_material",

    # Brand variations
    "brand": "brand",
    "brand_name": "brand",
    "manufacturer": "manufacturer",

    # Category variations
    "category": "category",
    "product_type": "product_type",
    "item_type": "item_type",
    "item_type_name": "item_type",
    "department": "department",

    # Image variations
    "main_image": "main_image_url",
    "main_image_url": "main_image_url",
    "image_url": "main_image_url",
    "other_images": "other_image_urls",
    "additional_images": "other_image_urls",

    # Quantity variations
    "quantity": "quantity",
    "stock_quantity": "quantity",
    "inventory": "quantity",
    "fulfillment_center_id": "fulfillment_center_id",

    # Weight variations
    "weight": "weight",
    "item_weight": "weight",
    "product_weight": "weight",
    "package_weight": "package_weight",

    # Dimensions
    "length": "length",
    "item_length": "length",
    "width": "width",
    "item_width": "width",
    "height": "height",
    "item_height": "height",
}

# Keywords for type inference
TYPE_KEYWORDS: Dict[str, List[str]] = {
    "int": ["quantity", "count", "number", "stock", "inventory", "units"],
    "float": ["price", "weight", "length", "width", "height", "mrp", "cost"],
    "date": ["date", "launch", "available", "expiry", "valid"],
    "boolean": ["is_", "has_", "can_", "enabled", "active"],
}


def normalize_header(header: str) -> str:
    """
    Normalize a header string to a canonical field name.

    Args:
        header: Raw header string from template

    Returns:
        Normalized canonical field name
    """
    if not header:
        return ""

    # Convert to lowercase and strip whitespace
    normalized = header.lower().strip()

    # Remove special characters except underscores
    normalized = re.sub(r"[^\w\s]", "", normalized)

    # Replace spaces with underscores
    normalized = re.sub(r"\s+", "_", normalized)

    # Remove leading/trailing underscores
    normalized = normalized.strip("_")

    # Look up in synonym map
    return SYNONYM_MAP.get(normalized, normalized)


def infer_type(header: str, canonical: str) -> str:
    """
    Infer the data type from header name.

    Args:
        header: Raw header string
        canonical: Canonical field name

    Returns:
        Inferred type: string, int, float, date, or boolean
    """
    header_lower = header.lower()
    canonical_lower = canonical.lower()

    for type_name, keywords in TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in header_lower or keyword in canonical_lower:
                return type_name

    return "string"


def detect_required(cell_value: str, secondary_row_value: Optional[str] = None) -> bool:
    """
    Detect if a field is required based on header indicators.

    Args:
        cell_value: The header cell value
        secondary_row_value: Optional value from a second header row

    Returns:
        True if field appears to be required
    """
    if not cell_value:
        return False

    cell_str = str(cell_value).lower()

    # Check for required indicators
    required_indicators = ["required", "*", "(required)", "[required]", "mandatory"]

    for indicator in required_indicators:
        if indicator in cell_str:
            return True

    # Check secondary row if provided
    if secondary_row_value:
        secondary_str = str(secondary_row_value).lower()
        for indicator in required_indicators:
            if indicator in secondary_str:
                return True

    return False


def extract_enum_values(cell_value: str) -> Optional[List[str]]:
    """
    Extract enum values if the header contains a list of valid values.

    Args:
        cell_value: The header or annotation cell value

    Returns:
        List of enum values or None
    """
    if not cell_value:
        return None

    # Look for patterns like "Values: A, B, C" or "[A|B|C]"
    patterns = [
        r"values?:\s*([^)]+)",
        r"\[([^\]]+)\]",
        r"\(([^)]+)\)",
    ]

    for pattern in patterns:
        match = re.search(pattern, str(cell_value), re.IGNORECASE)
        if match:
            values_str = match.group(1)
            # Split by comma, pipe, or semicolon
            values = re.split(r"[,|;]", values_str)
            values = [v.strip() for v in values if v.strip()]
            if len(values) > 1:
                return values

    return None


def find_header_row(ws: Worksheet) -> Tuple[int, Optional[int]]:
    """
    Find the header row(s) in a worksheet.

    Args:
        ws: openpyxl Worksheet object

    Returns:
        Tuple of (primary_header_row, secondary_header_row or None)
    """
    # Look for the first row with substantial content
    for row_idx in range(1, min(20, ws.max_row + 1)):
        non_empty_cells = sum(
            1 for cell in ws[row_idx] if cell.value and str(cell.value).strip()
        )

        # If row has multiple non-empty cells, likely a header
        if non_empty_cells >= 3:
            # Check if next row is also a header (e.g., contains "Required")
            if row_idx < ws.max_row:
                next_row = ws[row_idx + 1]
                next_row_str = " ".join(
                    str(cell.value or "") for cell in next_row
                ).lower()

                if "required" in next_row_str or "optional" in next_row_str:
                    return row_idx, row_idx + 1

            return row_idx, None

    return 1, None  # Default to first row


def parse_template(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse an Excel template and extract column definitions.

    Args:
        file_path: Path to the Excel file

    Returns:
        List of column definition dictionaries
    """
    wb = load_workbook(file_path, read_only=True, data_only=True)

    # Use the first worksheet
    ws = wb.active
    if ws is None:
        raise ValueError("No active worksheet found")

    # Find header rows
    header_row, secondary_row = find_header_row(ws)

    columns = []

    for col_idx, cell in enumerate(ws[header_row], start=0):
        header_value = cell.value

        if not header_value or not str(header_value).strip():
            continue

        header_str = str(header_value).strip()

        # Get secondary row value if exists
        secondary_value = None
        if secondary_row:
            secondary_cell = ws.cell(row=secondary_row, column=col_idx + 1)
            secondary_value = str(secondary_cell.value) if secondary_cell.value else None

        # Normalize to canonical name
        canonical = normalize_header(header_str)

        # Infer type
        field_type = infer_type(header_str, canonical)

        # Detect if required
        is_required = detect_required(header_str, secondary_value)

        # Extract enum values if present
        enum_values = extract_enum_values(header_str)
        if not enum_values and secondary_value:
            enum_values = extract_enum_values(secondary_value)

        columns.append({
            "col_index": col_idx,
            "header": header_str,
            "canonical": canonical,
            "type": field_type,
            "required": is_required,
            "enum": enum_values,
        })

    wb.close()
    return columns


def generate_schema_id(marketplace: str, category: str) -> str:
    """Generate a unique schema ID."""
    # Normalize marketplace and category
    marketplace_norm = re.sub(r"[^\w]", "", marketplace.lower())
    category_norm = re.sub(r"[^\w]", "", category.lower())
    return f"{marketplace_norm}_{category_norm}_v1"


def create_canonical_schema(
    file_path: str,
    marketplace: str,
    category: str,
) -> Dict[str, Any]:
    """
    Create a canonical schema from an Excel template.

    Args:
        file_path: Path to the Excel template
        marketplace: Marketplace name (e.g., 'amazon', 'flipkart')
        category: Product category (e.g., 'shirt', 'kurta')

    Returns:
        Canonical schema dictionary
    """
    columns = parse_template(file_path)

    schema_id = generate_schema_id(marketplace, category)

    # Detect if schema has variations (multiple SKUs per product)
    has_variations = any(
        col["canonical"] in ["parent_sku", "parent_child", "variation_theme"]
        for col in columns
    )

    schema = {
        "schema_id": schema_id,
        "marketplace": marketplace.lower(),
        "category": category.lower(),
        "version": date.today().isoformat(),
        "has_variations": has_variations,
        "columns": columns,
    }

    return schema


def save_schema(schema: Dict[str, Any], output_dir: Optional[str] = None) -> str:
    """
    Save schema to JSON file.

    Args:
        schema: Schema dictionary to save
        output_dir: Optional output directory path

    Returns:
        Path to saved schema file
    """
    if output_dir is None:
        # Default to project data directory
        output_dir = Path(__file__).parent.parent / "data" / "template_schemas"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / f"{schema['schema_id']}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    return str(file_path)


def main():
    """CLI entry point for template ingestion."""
    parser = argparse.ArgumentParser(
        description="Ingest marketplace Excel template and generate canonical schema"
    )
    parser.add_argument(
        "template_path",
        type=str,
        help="Path to the Excel template file (.xlsx or .xlsm)",
    )
    parser.add_argument(
        "marketplace",
        type=str,
        help="Marketplace name (e.g., amazon, flipkart)",
    )
    parser.add_argument(
        "category",
        type=str,
        help="Product category (e.g., shirt, kurta)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional output directory for schema JSON",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_output",
        help="Print schema to stdout instead of saving",
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.template_path):
        print(f"Error: Template file not found: {args.template_path}")
        return 1

    try:
        # Generate schema
        schema = create_canonical_schema(
            args.template_path,
            args.marketplace,
            args.category,
        )

        if args.print_output:
            print(json.dumps(schema, indent=2, ensure_ascii=False))
        else:
            output_path = save_schema(schema, args.output_dir)
            print(f"Schema saved to: {output_path}")
            print(f"Schema ID: {schema['schema_id']}")
            print(f"Columns extracted: {len(schema['columns'])}")

        return 0

    except Exception as e:
        print(f"Error processing template: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
