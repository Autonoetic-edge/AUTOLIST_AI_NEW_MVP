"""
Products API Router

Endpoints for querying synced products from the database.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..auth import get_current_user
from ..dependencies import get_database
from ..models import ShopifyProduct


router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[ShopifyProduct])
async def get_products(
    shop_domain: Optional[str] = Query(None, description="Filter by shop domain"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    limit: int = Query(50, ge=1, le=250, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get synced products from the database.
    
    Supports filtering by shop domain and product type, with pagination.
    """
    try:
        # Build query filter
        query = {}
        if shop_domain:
            query["shop_domain"] = shop_domain
        if product_type:
            query["product_type"] = {"$regex": product_type, "$options": "i"}
        
        # Query database with pagination
        cursor = db.products.find(query).skip(offset).limit(limit)
        products_list = await cursor.to_list(length=limit)
        
        # Transform to response model
        products = []
        for p in products_list:
            products.append(ShopifyProduct(
                id=str(p.get("shopify_id", p.get("_id", ""))),
                title=p.get("title", ""),
                description=p.get("body_html") or p.get("description"),
                vendor=p.get("vendor"),
                product_type=p.get("product_type"),
                tags=p.get("tags", []) if isinstance(p.get("tags"), list) else (p.get("tags", "").split(", ") if p.get("tags") else []),
                variants=p.get("variants", []),
                images=p.get("images", []),
                metafields=p.get("metafields"),
            ))
        
        return products
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch products: {str(e)}",
        )


@router.get("/count")
async def get_products_count(
    shop_domain: Optional[str] = Query(None, description="Filter by shop domain"),
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get total count of synced products.
    """
    try:
        query = {}
        if shop_domain:
            query["shop_domain"] = shop_domain
        
        count = await db.products.count_documents(query)
        return {"total_products": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to count products: {str(e)}",
        )


@router.get("/{product_id}", response_model=ShopifyProduct)
async def get_product_by_id(
    product_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get a single product by its Shopify ID.
    """
    try:
        # Search by shopify_id field
        product = await db.products.find_one({"shopify_id": product_id})
        
        if not product:
            # Try searching by MongoDB _id if not found
            from bson import ObjectId
            try:
                product = await db.products.find_one({"_id": ObjectId(product_id)})
            except:
                pass
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found",
            )
        
        return ShopifyProduct(
            id=str(product.get("shopify_id", product.get("_id", ""))),
            title=product.get("title", ""),
            description=product.get("body_html") or product.get("description"),
            vendor=product.get("vendor"),
            product_type=product.get("product_type"),
            tags=product.get("tags", []) if isinstance(product.get("tags"), list) else (product.get("tags", "").split(", ") if product.get("tags") else []),
            variants=product.get("variants", []),
            images=product.get("images", []),
            metafields=product.get("metafields"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product: {str(e)}",
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Delete a product from the database.
    """
    try:
        result = await db.products.delete_one({"shopify_id": product_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found",
            )
        
        return {"message": f"Product {product_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}",
        )
