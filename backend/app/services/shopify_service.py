"""
Shopify Integration Service

Handles connecting to Shopify stores, fetching products, and syncing data.
Uses real Shopify REST API and MongoDB for persistence.
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
        Fetch products from Shopify store using REST API.

        Args:
            limit: Number of products to fetch (max 250)
            page_info: Pagination cursor for next page

        Returns:
            List of product dictionaries from Shopify
        """
        all_products = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"limit": min(limit, 250)}
            if page_info:
                params["page_info"] = page_info

            try:
                response = await client.get(
                    f"{self.base_url}/products.json",
                    headers=self._get_headers(),
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                products = data.get("products", [])
                all_products.extend(products)
                
                print(f"Fetched {len(products)} products from Shopify")
                
            except httpx.HTTPStatusError as e:
                print(f"Shopify API error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Shopify API error: {e.response.status_code}")
            except Exception as e:
                print(f"Error fetching products: {e}")
                raise

        return all_products

    async def get_shop_info(self) -> Dict[str, Any]:
        """
        Get shop information from Shopify.

        Returns:
            Shop information dictionary
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/shop.json",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()
                return data.get("shop", {})
                
            except httpx.HTTPStatusError as e:
                print(f"Shopify API error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 401:
                    raise Exception("Invalid Shopify access token")
                raise Exception(f"Shopify API error: {e.response.status_code}")
            except Exception as e:
                print(f"Error fetching shop info: {e}")
                raise


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
        print("Warning: ENCRYPTION_KEY not set, storing token without encryption")
        return f"DEV:{token}"

    try:
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.encrypt(token.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return f"DEV:{token}"


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

    try:
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        raise ValueError("Failed to decrypt token")


async def save_shop_info(shop_domain: str, encrypted_token: str) -> bool:
    """
    Save shop connection info to MongoDB.

    Args:
        shop_domain: The Shopify store domain
        encrypted_token: Encrypted access token

    Returns:
        True if successful
    """
    from ..dependencies import get_database
    
    try:
        db = get_database()
        
        await db.shops.update_one(
            {"shop_domain": shop_domain},
            {
                "$set": {
                    "shop_domain": shop_domain,
                    "encrypted_token": encrypted_token,
                    "connected_at": datetime.utcnow(),
                    "status": "connected",
                }
            },
            upsert=True,
        )
        
        # Log activity
        await db.activity_log.insert_one({
            "type": "shop_connected",
            "message": f"Connected store: {shop_domain}",
            "shop_domain": shop_domain,
            "timestamp": datetime.utcnow(),
        })
        
        print(f"Saved shop info for {shop_domain}")
        return True
        
    except Exception as e:
        print(f"Error saving shop info: {e}")
        raise


async def get_shop_token(shop_domain: str) -> Optional[str]:
    """
    Retrieve and decrypt shop access token from MongoDB.

    Args:
        shop_domain: The Shopify store domain

    Returns:
        Decrypted access token or None if not found
    """
    from ..dependencies import get_database
    
    try:
        db = get_database()
        
        shop = await db.shops.find_one({"shop_domain": shop_domain})
        
        if shop and shop.get("encrypted_token"):
            return decrypt_token(shop["encrypted_token"])
        
        return None
        
    except RuntimeError as e:
        # Database not initialized - likely during startup
        print(f"Database not available: {e}")
        return None
    except Exception as e:
        print(f"Error getting shop token: {e}")
        return None


async def save_products(shop_domain: str, products: List[Dict[str, Any]]) -> int:
    """
    Save synced products to MongoDB.

    Args:
        shop_domain: The Shopify store domain
        products: List of product dictionaries from Shopify

    Returns:
        Number of products saved
    """
    from ..dependencies import get_database
    
    try:
        db = get_database()
        saved_count = 0
        
        for product in products:
            # Extract shopify_id from the product
            shopify_id = str(product.get("id", ""))
            
            # Prepare product document
            product_doc = {
                **product,
                "shop_domain": shop_domain,
                "shopify_id": shopify_id,
                "synced_at": datetime.utcnow(),
            }
            
            # Upsert product (update if exists, insert if not)
            result = await db.products.update_one(
                {"shop_domain": shop_domain, "shopify_id": shopify_id},
                {"$set": product_doc},
                upsert=True,
            )
            
            if result.upserted_id or result.modified_count > 0:
                saved_count += 1
        
        # Log activity
        await db.activity_log.insert_one({
            "type": "products_synced",
            "message": f"Synced {saved_count} products from {shop_domain}",
            "shop_domain": shop_domain,
            "products_count": saved_count,
            "timestamp": datetime.utcnow(),
        })
        
        # Update shop's last sync time
        await db.shops.update_one(
            {"shop_domain": shop_domain},
            {"$set": {"last_sync": datetime.utcnow(), "products_count": saved_count}}
        )
        
        print(f"Saved {saved_count} products for {shop_domain}")
        return saved_count
        
    except Exception as e:
        print(f"Error saving products: {e}")
        raise


async def get_connected_shops() -> List[Dict[str, Any]]:
    """
    Get list of all connected shops from database.

    Returns:
        List of shop documents
    """
    from ..dependencies import get_database
    
    try:
        db = get_database()
        cursor = db.shops.find({"status": "connected"})
        return await cursor.to_list(length=100)
    except Exception as e:
        print(f"Error getting connected shops: {e}")
        return []

