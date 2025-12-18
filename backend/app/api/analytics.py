"""
Analytics API Router

Endpoints for dashboard analytics and activity tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..auth import get_current_user
from ..dependencies import get_database
from ..models import AnalyticsSummary, ActivityLog


router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get analytics summary data for the dashboard.
    
    Returns counts of products, mapping jobs, and auto-fill rate.
    """
    try:
        # Get total products count
        total_products = await db.products.count_documents({})
        
        # Get mapping jobs counts by status
        # For now, we'll track basic stats - these can be expanded later
        mapping_jobs_pending = await db.mapping_jobs.count_documents({"status": "pending"}) if await collection_exists(db, "mapping_jobs") else 0
        mapping_jobs_needs_input = await db.mapping_jobs.count_documents({"status": "needs_input"}) if await collection_exists(db, "mapping_jobs") else 0
        mapping_jobs_completed = await db.mapping_jobs.count_documents({"status": "completed"}) if await collection_exists(db, "mapping_jobs") else 0
        
        # Get connected shops count
        connected_shops = await db.shops.count_documents({"status": "connected"}) if await collection_exists(db, "shops") else 0
        
        # Calculate auto-fill rate (placeholder - can be calculated based on actual mapping data)
        total_mappings = mapping_jobs_pending + mapping_jobs_needs_input + mapping_jobs_completed
        auto_fill_rate = 0.0
        if total_mappings > 0:
            auto_fill_rate = mapping_jobs_completed / total_mappings
        elif total_products > 0:
            # Default to a reasonable rate if we have products but no mappings yet
            auto_fill_rate = 0.0
        
        return AnalyticsSummary(
            total_products=total_products,
            mapping_jobs_pending=mapping_jobs_pending,
            mapping_jobs_needs_input=mapping_jobs_needs_input,
            mapping_jobs_completed=mapping_jobs_completed,
            auto_fill_rate=auto_fill_rate,
            connected_shops=connected_shops,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics summary: {str(e)}",
        )


@router.get("/activity", response_model=List[ActivityLog])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get recent activity log for the dashboard.
    
    Shows recent syncs, mappings, and other events.
    """
    try:
        activities = []
        
        # Get recent product syncs from activity_log collection
        if await collection_exists(db, "activity_log"):
            cursor = db.activity_log.find().sort("timestamp", -1).limit(limit)
            logs = await cursor.to_list(length=limit)
            
            for log in logs:
                activities.append(ActivityLog(
                    id=str(log.get("_id", "")),
                    type=log.get("type", "unknown"),
                    message=log.get("message", ""),
                    job_id=log.get("job_id"),
                    timestamp=log.get("timestamp", datetime.utcnow()),
                ))
        
        # If no activity log exists, generate from recent data
        if not activities:
            # Get recent product syncs
            if await collection_exists(db, "products"):
                cursor = db.products.find().sort("synced_at", -1).limit(5)
                recent_products = await cursor.to_list(length=5)
                
                for i, product in enumerate(recent_products):
                    synced_at = product.get("synced_at", datetime.utcnow())
                    activities.append(ActivityLog(
                        id=f"sync_{i}",
                        type="product_synced",
                        message=f"Synced product: {product.get('title', 'Unknown')}",
                        timestamp=synced_at if isinstance(synced_at, datetime) else datetime.utcnow(),
                    ))
            
            # Get recent shop connections
            if await collection_exists(db, "shops"):
                cursor = db.shops.find().sort("connected_at", -1).limit(3)
                recent_shops = await cursor.to_list(length=3)
                
                for i, shop in enumerate(recent_shops):
                    connected_at = shop.get("connected_at", datetime.utcnow())
                    activities.append(ActivityLog(
                        id=f"shop_{i}",
                        type="shop_connected",
                        message=f"Connected store: {shop.get('shop_domain', 'Unknown')}",
                        timestamp=connected_at if isinstance(connected_at, datetime) else datetime.utcnow(),
                    ))
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent activity: {str(e)}",
        )


@router.get("/mapping-stats")
async def get_mapping_stats(
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get detailed mapping statistics by status.
    """
    try:
        if not await collection_exists(db, "mapping_jobs"):
            return {
                "pending": 0,
                "processing": 0,
                "needs_user_input": 0,
                "ready": 0,
                "completed": 0,
                "error": 0,
            }
        
        # Aggregate by status
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        cursor = db.mapping_jobs.aggregate(pipeline)
        results = await cursor.to_list(length=100)
        
        stats = {
            "pending": 0,
            "processing": 0,
            "needs_user_input": 0,
            "ready": 0,
            "completed": 0,
            "error": 0,
        }
        
        for result in results:
            status_key = result["_id"]
            if status_key in stats:
                stats[status_key] = result["count"]
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mapping stats: {str(e)}",
        )


async def collection_exists(db: AsyncIOMotorDatabase, collection_name: str) -> bool:
    """Check if a collection exists in the database."""
    try:
        collections = await db.list_collection_names()
        return collection_name in collections
    except:
        return False
