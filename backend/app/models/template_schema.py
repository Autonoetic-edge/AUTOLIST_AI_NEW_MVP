"""
Template Schema MongoDB Model

Pydantic models and database helpers for template schemas.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError


class ColumnSchema(BaseModel):
    """Individual column definition in a template schema."""

    col_index: int = Field(description="Column index (0-based) in the template")
    header: str = Field(description="Original header text from template")
    canonical: str = Field(description="Normalized canonical field name")
    type: str = Field(default="string", description="Data type: string, int, float, date, boolean, enum")
    required: bool = Field(default=False, description="Whether field is required")
    enum: Optional[List[str]] = Field(default=None, description="Valid values for enum fields")


class TemplateSchemaModel(BaseModel):
    """Template schema for a marketplace category."""

    schema_id: str = Field(description="Unique schema identifier")
    marketplace: str = Field(description="Marketplace name (e.g., amazon, flipkart)")
    category: str = Field(description="Product category (e.g., shirt, kurta)")
    version: str = Field(description="Schema version (typically date-based)")
    has_variations: bool = Field(default=False, description="Whether schema supports parent-child variations")
    columns: List[ColumnSchema] = Field(description="List of column definitions")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "schema_id": "amazon_shirt_v1",
                "marketplace": "amazon",
                "category": "shirt",
                "version": "2024-01-15",
                "has_variations": True,
                "columns": [
                    {"col_index": 0, "header": "SKU", "canonical": "sku", "type": "string", "required": True},
                    {"col_index": 1, "header": "Title", "canonical": "title", "type": "string", "required": True},
                ],
            }
        }


def get_mongo_client(uri: str = "mongodb://localhost:27017") -> MongoClient:
    """
    Get MongoDB client.

    Args:
        uri: MongoDB connection URI

    Returns:
        MongoClient instance
    """
    return MongoClient(uri)


def get_template_schemas_collection(
    uri: str = "mongodb://localhost:27017",
    db_name: str = "autolist_ai",
) -> Collection:
    """
    Get the template_schemas collection.

    Args:
        uri: MongoDB connection URI
        db_name: Database name

    Returns:
        PyMongo Collection object
    """
    client = get_mongo_client(uri)
    db = client[db_name]
    return db["template_schemas"]


def insert_template_schema(
    schema: TemplateSchemaModel,
    uri: str = "mongodb://localhost:27017",
    db_name: str = "autolist_ai",
) -> str:
    """
    Insert a template schema into MongoDB.

    Args:
        schema: TemplateSchemaModel to insert
        uri: MongoDB connection URI
        db_name: Database name

    Returns:
        The schema_id of the inserted document

    Raises:
        DuplicateKeyError: If schema_id already exists
    """
    collection = get_template_schemas_collection(uri, db_name)

    # Prepare document
    doc = schema.model_dump()
    doc["_id"] = schema.schema_id
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()

    try:
        collection.insert_one(doc)
        return schema.schema_id
    except DuplicateKeyError:
        # Update existing schema
        doc.pop("_id")
        doc.pop("created_at")
        doc["updated_at"] = datetime.utcnow()

        collection.update_one(
            {"_id": schema.schema_id},
            {"$set": doc},
        )
        return schema.schema_id


def get_template_schema(
    schema_id: str,
    uri: str = "mongodb://localhost:27017",
    db_name: str = "autolist_ai",
) -> Optional[TemplateSchemaModel]:
    """
    Get a template schema by ID.

    Args:
        schema_id: Schema identifier
        uri: MongoDB connection URI
        db_name: Database name

    Returns:
        TemplateSchemaModel or None if not found
    """
    collection = get_template_schemas_collection(uri, db_name)

    doc = collection.find_one({"_id": schema_id})
    if not doc:
        return None

    # Remove MongoDB _id before converting to model
    doc["schema_id"] = doc.pop("_id")

    return TemplateSchemaModel(**doc)


def list_template_schemas(
    marketplace: Optional[str] = None,
    category: Optional[str] = None,
    uri: str = "mongodb://localhost:27017",
    db_name: str = "autolist_ai",
) -> List[TemplateSchemaModel]:
    """
    List template schemas with optional filtering.

    Args:
        marketplace: Filter by marketplace name
        category: Filter by category
        uri: MongoDB connection URI
        db_name: Database name

    Returns:
        List of TemplateSchemaModel objects
    """
    collection = get_template_schemas_collection(uri, db_name)

    query: Dict[str, Any] = {}
    if marketplace:
        query["marketplace"] = marketplace.lower()
    if category:
        query["category"] = category.lower()

    schemas = []
    for doc in collection.find(query):
        doc["schema_id"] = doc.pop("_id")
        schemas.append(TemplateSchemaModel(**doc))

    return schemas


def delete_template_schema(
    schema_id: str,
    uri: str = "mongodb://localhost:27017",
    db_name: str = "autolist_ai",
) -> bool:
    """
    Delete a template schema by ID.

    Args:
        schema_id: Schema identifier
        uri: MongoDB connection URI
        db_name: Database name

    Returns:
        True if deleted, False if not found
    """
    collection = get_template_schemas_collection(uri, db_name)

    result = collection.delete_one({"_id": schema_id})
    return result.deleted_count > 0
