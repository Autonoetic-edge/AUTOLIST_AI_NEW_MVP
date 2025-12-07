"""
Shopify API Router

Endpoints for connecting Shopify stores and syncing products.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..auth import get_current_user
from ..models import (
    ShopifyConnectRequest,
    ShopifyConnectResponse,
    ShopifySyncRequest,
    ShopifySyncResponse,
    ShopifyProduct,
)
from ..services.shopify_service import (
    ShopifyService,
    encrypt_token,
    save_shop_info,
    get_shop_token,
    save_products,
)


router = APIRouter(prefix="/api/shopify", tags=["Shopify"])


@router.post("/connect", response_model=ShopifyConnectResponse)
async def connect_shopify_store(
    request: ShopifyConnectRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Connect a Shopify store by saving its access token.

    This endpoint validates the connection and stores the encrypted access token
    for future API calls.
    """
    try:
        # Initialize service to validate connection
        service = ShopifyService(request.shop_domain, request.access_token)

        # Verify connection by fetching shop info
        shop_info = await service.get_shop_info()

        if not shop_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not connect to Shopify store. Please verify credentials.",
            )

        # Encrypt and save the access token
        encrypted_token = encrypt_token(request.access_token)
        await save_shop_info(request.shop_domain, encrypted_token)

        return ShopifyConnectResponse(
            success=True,
            shop_domain=request.shop_domain,
            message=f"Successfully connected to {shop_info.get('name', request.shop_domain)}",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect Shopify store: {str(e)}",
        )


@router.post("/sync-products", response_model=ShopifySyncResponse)
async def sync_products(
    request: ShopifySyncRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Sync products from a connected Shopify store.

    Fetches all products from the Shopify store and saves them to the database
    for mapping and processing.
    """
    try:
        # Get the stored access token for this shop
        access_token = await get_shop_token(request.shop_domain)

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shop {request.shop_domain} is not connected. Please connect first.",
            )

        # Initialize service and fetch products
        service = ShopifyService(request.shop_domain, access_token)
        products_data = await service.fetch_products(limit=250)

        # Save products to database
        saved_count = await save_products(request.shop_domain, products_data)

        # Convert to response models
        products = [
            ShopifyProduct(
                id=str(p.get("id", "")),
                title=p.get("title", ""),
                description=p.get("description"),
                vendor=p.get("vendor"),
                product_type=p.get("product_type"),
                tags=p.get("tags", []),
                variants=p.get("variants", []),
                images=p.get("images", []),
                metafields=p.get("metafields"),
            )
            for p in products_data
        ]

        return ShopifySyncResponse(
            success=True,
            products_count=saved_count,
            products=products,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync products: {str(e)}",
        )


@router.get("/products", response_model=List[ShopifyProduct])
async def get_products(
    shop_domain: str,
    limit: int = 50,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
):
    """
    Get synced products from database.

    TODO: Implement MongoDB query with pagination
    """
    # TODO: Implement actual database query
    # Example:
    # from ..dependencies import get_database
    # db = await get_database()
    # products = await db.products.find(
    #     {"shop_domain": shop_domain}
    # ).skip(offset).limit(limit).to_list(limit)

    # Return sample products for development
    access_token = await get_shop_token(shop_domain)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop {shop_domain} is not connected.",
        )

    service = ShopifyService(shop_domain, access_token)
    products_data = await service.fetch_products(limit=limit)

    return [
        ShopifyProduct(
            id=str(p.get("id", "")),
            title=p.get("title", ""),
            description=p.get("description"),
            vendor=p.get("vendor"),
            product_type=p.get("product_type"),
            tags=p.get("tags", []),
            variants=p.get("variants", []),
            images=p.get("images", []),
            metafields=p.get("metafields"),
        )
        for p in products_data
    ]


@router.get("/status/{shop_domain}")
async def get_shop_status(
    shop_domain: str,
    current_user: str = Depends(get_current_user),
):
    """
    Get connection status for a Shopify store.
    """
    access_token = await get_shop_token(shop_domain)

    if not access_token:
        return {
            "shop_domain": shop_domain,
            "connected": False,
            "message": "Store not connected",
        }

    return {
        "shop_domain": shop_domain,
        "connected": True,
        "message": "Store connected and ready",
    }
