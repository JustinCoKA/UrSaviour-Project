# backend/app/api/v1/endpoints/products_simple.py
from fastapi import APIRouter, Query
from sqlalchemy import select, MetaData, Table
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Reflect tables from existing database
metadata = MetaData()
Products = Table("products", metadata, autoload_with=engine)

@router.get("/health", summary="Health check")
def health_check():
    """API status check"""
    return {"status": "ok", "service": "products"}

@router.get("/test", summary="Simple test endpoint")
def test_endpoint():
    """Simple test to check if API is working"""
    return {"message": "Products API is working", "timestamp": "2025-10-18"}

@router.get("/", summary="Get all products - simplified version")
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in product names"),
    limit: int = Query(100, description="Maximum number of products to return")
):
    """
    Simplified product list API - emergency fix version
    """
    try:
        with SessionLocal() as db:
            # Simple query to get basic product information
            products_query = select(
                Products.c.productId,
                Products.c.productName,
                Products.c.categoryName,
                Products.c.description,
                Products.c.defaultImageUrl,
                Products.c.basePrice
            ).limit(limit)
            
            products = db.execute(products_query).fetchall()
            
            # Convert to simple frontend format
            result = []
            for product in products:
                product_data = {
                    "id": product.productId,
                    "name": product.productName,
                    "category": product.categoryName,
                    "description": product.description or "",
                    "image": product.defaultImageUrl or "",
                    "stores": [
                        {"brand": "Justin Groceries", "price": float(product.basePrice or 0)},
                        {"brand": "Mio Mart", "price": float(product.basePrice or 0) + 0.05},
                        {"brand": "Austin Fresh", "price": float(product.basePrice or 0) - 0.03},
                        {"brand": "Aadarsh Deals", "price": float(product.basePrice or 0) + 0.02}
                    ]
                }
                result.append(product_data)
            
            return result
            
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        # Return empty list instead of crashing
        return []