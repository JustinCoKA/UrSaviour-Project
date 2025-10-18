# backend/app/api/v1/endpoints/products.py
# Main Products API endpoint using real database structure
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
Stores = Table("stores", metadata, autoload_with=engine)
StoreBasePrices = Table("store_base_prices", metadata, autoload_with=engine)
StoreOfferings = Table("storeOfferings", metadata, autoload_with=engine)

@router.get("/health", summary="Health check")
def health_check():
    """API status check"""
    return {"status": "ok", "service": "products"}

@router.get("/test", summary="Simple test endpoint")
def test_endpoint():
    """Simple test to check if API is working"""
    return {"message": "Products API is working", "timestamp": "2025-10-18"}

@router.get("/", summary="Get all products - using real database structure")
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in product names"),
    limit: int = Query(100, description="Maximum number of products to return")
):
    """
    Product list API using actual database structure:
    - products: basic product info
    - store_base_prices: real store-specific prices  
    - storeOfferings: discount information (when available)
    """
    try:
        with SessionLocal() as db:
            # Get basic product information
            products_query = select(
                Products.c.productId,
                Products.c.productName,
                Products.c.categoryName,
                Products.c.description,
                Products.c.defaultImageUrl,
                Products.c.basePrice
            ).limit(limit)
            
            products = db.execute(products_query).fetchall()
            
            # Get all stores
            stores_query = select(Stores.c.storeId, Stores.c.storeName)
            stores = db.execute(stores_query).fetchall()
            stores_dict = {store.storeId: store.storeName for store in stores}
            
            result = []
            for product in products:
                # Get store-specific base prices for this product
                base_prices_query = select(
                    StoreBasePrices.c.storeId,
                    StoreBasePrices.c.basePrice
                ).where(StoreBasePrices.c.productId == product.productId)
                
                base_prices = db.execute(base_prices_query).fetchall()
                base_prices_dict = {bp.storeId: float(bp.basePrice) for bp in base_prices}
                
                # Get any discount offerings for this product
                offerings_query = select(
                    StoreOfferings.c.storeId,
                    StoreOfferings.c.price,
                    StoreOfferings.c.basePrice,
                    StoreOfferings.c.offerDetails
                ).where(StoreOfferings.c.productId == product.productId)
                
                offerings = db.execute(offerings_query).fetchall()
                offerings_dict = {off.storeId: off for off in offerings}
                
                # Build stores array with real prices
                stores_info = []
                special_offer = None
                
                for store_id, store_name in stores_dict.items():
                    # Get base price for this store
                    base_price = base_prices_dict.get(store_id, float(product.basePrice or 0))
                    
                    # Check for discount offering
                    offering = offerings_dict.get(store_id)
                    if offering and offering.price:
                        # There's a discount
                        final_price = float(offering.price)
                        original_price = float(offering.basePrice or base_price)
                        
                        store_data = {
                            "brand": store_name,
                            "price": final_price,
                            "original_price": original_price
                        }
                        
                        # Set special offer info (first one found)
                        if special_offer is None and offering.offerDetails:
                            special_offer = {
                                "type": offering.offerDetails,
                                "store": store_name
                            }
                    else:
                        # No discount, use base price
                        store_data = {
                            "brand": store_name,
                            "price": base_price
                        }
                    
                    stores_info.append(store_data)
                
                # Create product data
                product_data = {
                    "id": product.productId,
                    "name": product.productName,
                    "category": product.categoryName,
                    "description": product.description or "",
                    "image": product.defaultImageUrl or "",
                    "stores": stores_info
                }
                
                # Add special offer if any discount exists
                if special_offer:
                    product_data["special"] = special_offer
                
                result.append(product_data)
            
            return result
            
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        # Return error info for debugging
        return {"error": str(e), "message": "Database query failed"}