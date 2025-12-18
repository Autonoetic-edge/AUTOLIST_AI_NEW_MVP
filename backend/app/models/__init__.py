"""Data models for AutoList AI."""
from .template_schema import (
    ColumnSchema,
    TemplateSchemaModel,
    insert_template_schema,
    get_template_schema,
    list_template_schemas,
)

# Import models from the parent models.py file
# These are imported by other modules like auth.py
import sys
import os
import importlib.util

# Load the models.py file (not the models/ package)
_models_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models.py')
_spec = importlib.util.spec_from_file_location("_models_module", _models_path)
_models_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_models_module)

# Re-export all the models
TokenResponse = _models_module.TokenResponse
TokenPayload = _models_module.TokenPayload
UserCreate = _models_module.UserCreate
UserLogin = _models_module.UserLogin
UserResponse = _models_module.UserResponse
ShopifyConnectRequest = _models_module.ShopifyConnectRequest
ShopifyConnectResponse = _models_module.ShopifyConnectResponse
ShopifySyncRequest = _models_module.ShopifySyncRequest
ShopifyProduct = _models_module.ShopifyProduct
ShopifySyncResponse = _models_module.ShopifySyncResponse
TemplateSchema = _models_module.TemplateSchema
MappingStatus = _models_module.MappingStatus
MappingField = _models_module.MappingField
MappingResult = _models_module.MappingResult
MappingUpdateRequest = _models_module.MappingUpdateRequest
AnalyticsSummary = _models_module.AnalyticsSummary
ActivityLog = _models_module.ActivityLog
ValidationError = _models_module.ValidationError
ValidationResult = _models_module.ValidationResult

__all__ = [
    # Template Schema models (from template_schema.py)
    "ColumnSchema",
    "TemplateSchemaModel",
    "insert_template_schema",
    "get_template_schema",
    "list_template_schemas",
    # Auth models
    "TokenResponse",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    # Shopify models
    "ShopifyConnectRequest",
    "ShopifyConnectResponse",
    "ShopifySyncRequest",
    "ShopifyProduct",
    "ShopifySyncResponse",
    # Template Schema (API model)
    "TemplateSchema",
    # Mapping models
    "MappingStatus",
    "MappingField",
    "MappingResult",
    "MappingUpdateRequest",
    # Analytics models
    "AnalyticsSummary",
    "ActivityLog",
    # Validation models
    "ValidationError",
    "ValidationResult",
]

