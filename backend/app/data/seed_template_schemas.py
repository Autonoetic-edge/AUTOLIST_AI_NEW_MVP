#!/usr/bin/env python3
"""
Seed Template Schemas

Script to populate MongoDB with sample template schemas for testing.
Creates schemas for Amazon Shirt and Amazon Kurta categories.

Usage:
    python -m app.data.seed_template_schemas [--uri mongodb://localhost:27017]
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

from pymongo import MongoClient


# Sample schema for Amazon Shirt category
AMAZON_SHIRT_SCHEMA = {
    "_id": "amazon_shirt_v1",
    "schema_id": "amazon_shirt_v1",
    "marketplace": "amazon",
    "category": "shirt",
    "version": "2024-01-15",
    "has_variations": True,
    "columns": [
        {
            "col_index": 0,
            "header": "SKU",
            "canonical": "sku",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 1,
            "header": "Parent SKU",
            "canonical": "parent_sku",
            "type": "string",
            "required": False,
            "enum": None,
        },
        {
            "col_index": 2,
            "header": "Product Title",
            "canonical": "title",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 3,
            "header": "Product Description",
            "canonical": "description",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 4,
            "header": "Brand",
            "canonical": "brand",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 5,
            "header": "Fabric Type",
            "canonical": "fabric",
            "type": "string",
            "required": True,
            "enum": ["Cotton", "Polyester", "Silk", "Linen", "Rayon", "Blend"],
        },
        {
            "col_index": 6,
            "header": "Size",
            "canonical": "size",
            "type": "string",
            "required": True,
            "enum": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"],
        },
        {
            "col_index": 7,
            "header": "Color",
            "canonical": "color",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 8,
            "header": "Price",
            "canonical": "price",
            "type": "float",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 9,
            "header": "Main Image URL",
            "canonical": "main_image_url",
            "type": "string",
            "required": True,
            "enum": None,
        },
    ],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}


# Sample schema for Amazon Kurta category
AMAZON_KURTA_SCHEMA = {
    "_id": "amazon_kurta_v1",
    "schema_id": "amazon_kurta_v1",
    "marketplace": "amazon",
    "category": "kurta",
    "version": "2024-01-15",
    "has_variations": True,
    "columns": [
        {
            "col_index": 0,
            "header": "SKU",
            "canonical": "sku",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 1,
            "header": "Parent SKU",
            "canonical": "parent_sku",
            "type": "string",
            "required": False,
            "enum": None,
        },
        {
            "col_index": 2,
            "header": "Product Title",
            "canonical": "title",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 3,
            "header": "Product Description",
            "canonical": "description",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 4,
            "header": "Brand",
            "canonical": "brand",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 5,
            "header": "Fabric Type",
            "canonical": "fabric",
            "type": "string",
            "required": True,
            "enum": ["Cotton", "Silk", "Rayon", "Linen", "Polyester", "Blend", "Khadi"],
        },
        {
            "col_index": 6,
            "header": "Size",
            "canonical": "size",
            "type": "string",
            "required": True,
            "enum": ["36", "38", "40", "42", "44", "46", "48"],
        },
        {
            "col_index": 7,
            "header": "Color",
            "canonical": "color",
            "type": "string",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 8,
            "header": "Price",
            "canonical": "price",
            "type": "float",
            "required": True,
            "enum": None,
        },
        {
            "col_index": 9,
            "header": "Occasion",
            "canonical": "occasion",
            "type": "string",
            "required": False,
            "enum": ["Casual", "Festive", "Wedding", "Party", "Formal"],
        },
    ],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}


def seed_schemas(
    uri: str = "mongodb://localhost:27017",
    db_name: str = "autolist_ai",
) -> dict:
    """
    Seed template schemas into MongoDB.

    Args:
        uri: MongoDB connection URI
        db_name: Database name

    Returns:
        Dictionary with seeding results
    """
    client = MongoClient(uri)
    db = client[db_name]
    collection = db["template_schemas"]

    results = {
        "inserted": [],
        "updated": [],
        "errors": [],
    }

    schemas = [AMAZON_SHIRT_SCHEMA, AMAZON_KURTA_SCHEMA]

    for schema in schemas:
        schema_id = schema["_id"]
        try:
            # Check if schema exists
            existing = collection.find_one({"_id": schema_id})

            if existing:
                # Update existing schema
                schema["updated_at"] = datetime.utcnow()
                schema_copy = schema.copy()
                schema_copy.pop("created_at", None)  # Don't update created_at

                collection.update_one(
                    {"_id": schema_id},
                    {"$set": schema_copy},
                )
                results["updated"].append(schema_id)
                print(f"Updated: {schema_id}")
            else:
                # Insert new schema
                collection.insert_one(schema)
                results["inserted"].append(schema_id)
                print(f"Inserted: {schema_id}")

        except Exception as e:
            results["errors"].append({"schema_id": schema_id, "error": str(e)})
            print(f"Error with {schema_id}: {e}")

    # Also save as JSON files for reference
    output_dir = Path(__file__).parent / "template_schemas"
    output_dir.mkdir(parents=True, exist_ok=True)

    for schema in schemas:
        schema_copy = schema.copy()
        schema_copy.pop("_id", None)
        schema_copy.pop("created_at", None)
        schema_copy.pop("updated_at", None)

        json_path = output_dir / f"{schema['schema_id']}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(schema_copy, f, indent=2, ensure_ascii=False)

        print(f"Saved JSON: {json_path}")

    client.close()
    return results


def main():
    """CLI entry point for seeding schemas."""
    parser = argparse.ArgumentParser(
        description="Seed template schemas into MongoDB"
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="mongodb://localhost:27017",
        help="MongoDB connection URI",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="autolist_ai",
        help="Database name",
    )

    args = parser.parse_args()

    print(f"Seeding schemas to {args.uri}/{args.db}...")
    results = seed_schemas(args.uri, args.db)

    print("\n--- Results ---")
    print(f"Inserted: {len(results['inserted'])}")
    print(f"Updated: {len(results['updated'])}")
    print(f"Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"  - {error['schema_id']}: {error['error']}")


if __name__ == "__main__":
    main()
