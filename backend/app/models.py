"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Authentication Models
# ============================================================================

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiry in seconds")


class TokenPayload(BaseModel):
    """JWT token payload data."""
    sub: str  # user_id
    exp: datetime
    iat: datetime


class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8)
    name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response (excludes sensitive data)."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    created_at: datetime


# ============================================================================
# Shopify Models
# ============================================================================

class ShopifyConnectRequest(BaseModel):
    """Request to connect a Shopify store."""
    shop_domain: str = Field(description="Shopify store domain (e.g., mystore.myshopify.com)")
    access_token: str = Field(description="Shopify access token")


class ShopifyConnectResponse(BaseModel):
    """Response after connecting Shopify store."""
    success: bool
    shop_domain: str
    message: str


class ShopifySyncRequest(BaseModel):
    """Request to sync products from Shopify."""
    shop_domain: str


class ShopifyProduct(BaseModel):
    """Shopify product representation."""
    id: str
    title: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = []
    variants: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []
    metafields: Optional[Dict[str, Any]] = None


class ShopifySyncResponse(BaseModel):
    """Response after syncing products."""
    success: bool
    products_count: int
    products: List[ShopifyProduct]


# ============================================================================
# Template Schema Models
# ============================================================================

class ColumnSchema(BaseModel):
    """Individual column in a template schema."""
    col_index: int
    header: str
    canonical: str
    type: str = "string"  # string, int, float, date, enum
    required: bool = False
    enum: Optional[List[str]] = None


class TemplateSchema(BaseModel):
    """Template schema for a marketplace category."""
    schema_id: str
    marketplace: str
    category: str
    version: str
    has_variations: bool = False
    columns: List[ColumnSchema]


# ============================================================================
# Mapping Models
# ============================================================================

class MappingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    NEEDS_USER_INPUT = "needs_user_input"
    READY = "ready"
    COMPLETED = "completed"
    ERROR = "error"


class MappingField(BaseModel):
    """Individual field mapping result."""
    value: Optional[Any] = None
    source: str = Field(description="Source: shopify, title, description, metafield, ai")
    confidence: float = Field(ge=0.0, le=1.0)


class MappingResult(BaseModel):
    """Complete mapping result for a product."""
    job_id: str
    product_id: str
    template_schema_id: str
    status: MappingStatus
    mappings: Dict[str, MappingField]
    errors: List[str] = []
    created_at: datetime
    updated_at: datetime


class MappingUpdateRequest(BaseModel):
    """Request to update mapping fields (user edits)."""
    job_id: str
    updates: Dict[str, Any]


# ============================================================================
# Analytics Models
# ============================================================================

class AnalyticsSummary(BaseModel):
    """Dashboard analytics summary."""
    total_products: int
    mapping_jobs_pending: int = 0
    mapping_jobs_needs_input: int = 0
    mapping_jobs_completed: int = 0
    auto_fill_rate: float = Field(default=0.0, description="Average confidence score")
    connected_shops: int = 0
    recent_activity: Optional[List[Dict[str, Any]]] = None


class ActivityLog(BaseModel):
    """Activity log entry for dashboard."""
    id: str
    type: str = Field(description="Activity type: product_synced, shop_connected, mapping_completed, etc.")
    message: str
    job_id: Optional[str] = None
    timestamp: datetime


# ============================================================================
# Validation Models
# ============================================================================

class ValidationError(BaseModel):
    """Validation error for a field."""
    field: str
    message: str
    value: Optional[Any] = None


class ValidationResult(BaseModel):
    """Validation result for a mapping."""
    valid: bool
    errors: List[ValidationError]
