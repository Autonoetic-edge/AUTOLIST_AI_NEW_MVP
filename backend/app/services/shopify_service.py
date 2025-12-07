"""
Shopify Integration Service

Handles connecting to Shopify stores, fetching products, and syncing data.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from cryptography.fernet import Fernet

from ..config import settings


class ShopifyService:
    """Service for interacting with Shopify API."""

    def __init__(self, shop_domain: str, access_token: str):
        """
        Initialize Shopify service for a specific shop.

        Args:
            shop_domain: The Shopify store domain (e.g., mystore.myshopify.com)
            access_token: The Shopify access token
        """
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.api_version = settings.SHOPIFY_API_VERSION
        self.base_url = f"https://{shop_domain}/admin/api/{self.api_version}"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Shopify API requests."""
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    async def fetch_products(
        self,
        limit: int = 50,
        page_info: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch products from Shopify store.

        Args:
            limit: Number of products to fetch (max 250)
            page_info: Pagination cursor for next page

        Returns:
            List of product dictionaries

        TODO: Implement actual Shopify API call
        """
        # TODO: Replace with actual Shopify GraphQL or REST API call
        # Example implementation:
        #
        # async with httpx.AsyncClient() as client:
        #     params = {"limit": min(limit, 250)}
        #     if page_info:
        #         params["page_info"] = page_info
        #
        #     response = await client.get(
        #         f"{self.base_url}/products.json",
        #         headers=self._get_headers(),
        #         params=params,
        #     )
        #     response.raise_for_status()
        #     data = response.json()
        #     return data.get("products", [])

        # Return sample products for development
        return [
            {
                "id": "gid://shopify/Product/123456789",
                "title": "Premium Cotton T-Shirt - Blue",
                "description": "100% organic cotton t-shirt. Soft, breathable fabric perfect for summer. Machine washable.",
                "vendor": "AutoList Fashion",
                "product_type": "Shirt",
                "tags": ["cotton", "summer", "casual", "blue"],
                "handle": "premium-cotton-tshirt-blue",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:22:00Z",
                "variants": [
                    {
                        "id": "gid://shopify/ProductVariant/111",
                        "title": "Small",
                        "sku": "PCTS-BLU-S",
                        "price": "29.99",
                        "compare_at_price": "39.99",
                        "inventory_quantity": 50,
                        "option1": "Small",
                        "option2": "Blue",
                        "weight": 200,
                        "weight_unit": "g",
                    },
                    {
                        "id": "gid://shopify/ProductVariant/112",
                        "title": "Medium",
                        "sku": "PCTS-BLU-M",
                        "price": "29.99",
                        "compare_at_price": "39.99",
                        "inventory_quantity": 75,
                        "option1": "Medium",
                        "option2": "Blue",
                        "weight": 220,
                        "weight_unit": "g",
                    },
                    {
                        "id": "gid://shopify/ProductVariant/113",
                        "title": "Large",
                        "sku": "PCTS-BLU-L",
                        "price": "29.99",
                        "compare_at_price": "39.99",
                        "inventory_quantity": 60,
                        "option1": "Large",
                        "option2": "Blue",
                        "weight": 240,
                        "weight_unit": "g",
                    },
                ],
                "images": [
                    {
                        "id": "gid://shopify/ProductImage/1",
                        "src": "https://example.com/images/tshirt-blue-1.jpg",
                        "alt": "Blue cotton t-shirt front view",
                    }
                ],
                "options": [
                    {"name": "Size", "values": ["Small", "Medium", "Large"]},
                    {"name": "Color", "values": ["Blue"]},
                ],
                "metafields": {
                    "custom": {
                        "fabric_composition": "100% Organic Cotton",
                        "care_instructions": "Machine wash cold, tumble dry low",
                        "country_of_origin": "India",
                    }
                },
            },
            {
                "id": "gid://shopify/Product/987654321",
                "title": "Traditional Silk Kurta - Maroon",
                "description": "Elegant silk kurta with intricate embroidery. Perfect for festivals and special occasions. Dry clean only.",
                "vendor": "AutoList Fashion",
                "product_type": "Kurta",
                "tags": ["silk", "festive", "ethnic", "maroon", "embroidered"],
                "handle": "traditional-silk-kurta-maroon",
                "created_at": "2024-02-01T09:00:00Z",
                "updated_at": "2024-02-10T11:15:00Z",
                "variants": [
                    {
                        "id": "gid://shopify/ProductVariant/221",
                        "title": "38",
                        "sku": "TSK-MAR-38",
                        "price": "89.99",
                        "compare_at_price": "119.99",
                        "inventory_quantity": 25,
                        "option1": "38",
                        "option2": "Maroon",
                        "weight": 350,
                        "weight_unit": "g",
                    },
                    {
                        "id": "gid://shopify/ProductVariant/222",
                        "title": "40",
                        "sku": "TSK-MAR-40",
                        "price": "89.99",
                        "compare_at_price": "119.99",
                        "inventory_quantity": 30,
                        "option1": "40",
                        "option2": "Maroon",
                        "weight": 370,
                        "weight_unit": "g",
                    },
                ],
                "images": [
                    {
                        "id": "gid://shopify/ProductImage/2",
                        "src": "https://example.com/images/kurta-maroon-1.jpg",
                        "alt": "Maroon silk kurta front view",
                    }
                ],
                "options": [
                    {"name": "Size", "values": ["38", "40", "42", "44"]},
                    {"name": "Color", "values": ["Maroon"]},
                ],
                "metafields": {
                    "custom": {
                        "fabric_composition": "100% Pure Silk",
                        "care_instructions": "Dry clean only",
                        "country_of_origin": "India",
                        "occasion": "Festive, Wedding, Party",
                    }
                },
            },
        ]

    async def get_shop_info(self) -> Dict[str, Any]:
        """
        Get shop information from Shopify.

        Returns:
            Shop information dictionary

        TODO: Implement actual Shopify API call
        """
        # TODO: Replace with actual API call
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{self.base_url}/shop.json",
        #         headers=self._get_headers(),
        #     )
        #     response.raise_for_status()
        #     return response.json().get("shop", {})

        return {
            "id": 12345,
            "name": "Demo Store",
            "email": "demo@example.com",
            "domain": self.shop_domain,
            "currency": "USD",
            "timezone": "America/New_York",
        }


def encrypt_token(token: str) -> str:
    """
    Encrypt an access token for secure storage.

    Args:
        token: Plain text access token

    Returns:
        Encrypted token string
    """
    if not settings.ENCRYPTION_KEY:
        # In development, return as-is with a warning prefix
        return f"DEV:{token}"

    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt an encrypted access token.

    Args:
        encrypted_token: Encrypted token string

    Returns:
        Plain text access token
    """
    if encrypted_token.startswith("DEV:"):
        # Development token - return without encryption
        return encrypted_token[4:]

    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not configured")

    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.decrypt(encrypted_token.encode()).decode()


async def save_shop_info(shop_domain: str, encrypted_token: str) -> bool:
    """
    Save shop connection info to database.

    Args:
        shop_domain: The Shopify store domain
        encrypted_token: Encrypted access token

    Returns:
        True if successful

    TODO: Implement actual MongoDB persistence
    """
    # TODO: Implement MongoDB save
    # Example:
    # from ..dependencies import get_database
    # db = await get_database()
    # await db.shops.update_one(
    #     {"shop_domain": shop_domain},
    #     {
    #         "$set": {
    #             "shop_domain": shop_domain,
    #             "encrypted_token": encrypted_token,
    #             "connected_at": datetime.utcnow(),
    #             "status": "connected",
    #         }
    #     },
    #     upsert=True,
    # )

    print(f"[MOCK] Saving shop info for {shop_domain}")
    return True


async def get_shop_token(shop_domain: str) -> Optional[str]:
    """
    Retrieve and decrypt shop access token from database.

    Args:
        shop_domain: The Shopify store domain

    Returns:
        Decrypted access token or None if not found

    TODO: Implement actual MongoDB lookup
    """
    # TODO: Implement MongoDB lookup
    # Example:
    # from ..dependencies import get_database
    # db = await get_database()
    # shop = await db.shops.find_one({"shop_domain": shop_domain})
    # if shop:
    #     return decrypt_token(shop["encrypted_token"])

    # Return mock token for development
    return "mock_access_token_for_development"


async def save_products(shop_domain: str, products: List[Dict[str, Any]]) -> int:
    """
    Save synced products to database.

    Args:
        shop_domain: The Shopify store domain
        products: List of product dictionaries

    Returns:
        Number of products saved

    TODO: Implement actual MongoDB persistence
    """
    # TODO: Implement MongoDB bulk save
    # Example:
    # from ..dependencies import get_database
    # db = await get_database()
    # for product in products:
    #     await db.products.update_one(
    #         {"shop_domain": shop_domain, "shopify_id": product["id"]},
    #         {
    #             "$set": {
    #                 **product,
    #                 "shop_domain": shop_domain,
    #                 "synced_at": datetime.utcnow(),
    #             }
    #         },
    #         upsert=True,
    #     )

    print(f"[MOCK] Saving {len(products)} products for {shop_domain}")
    return len(products)
