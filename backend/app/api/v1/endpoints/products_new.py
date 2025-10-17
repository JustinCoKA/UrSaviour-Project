# backend/app/api/v1/endpoints/products_new.py
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, func, MetaData, Table, and_, or_
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
StoreOfferings = Table("storeOfferings", metadata, autoload_with=engine)

@router.get("/", summary="Get all products with store prices")
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in product names"),
    store_id: Optional[int] = Query(None, description="Filter by specific store"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    on_sale: Optional[bool] = Query(None, description="Filter products on sale"),
    limit: int = Query(100, description="Maximum number of products to return")
) -> Dict[str, Any]:
    """
    프론트엔드 요구사항에 맞춘 제품 목록 API
    각 제품마다 모든 매장의 가격 정보를 포함하여 반환
    """
    
    with SessionLocal() as db:
        try:
            # 기본 제품 정보 가져오기
            products_query = select(
                Products.c.productId,
                Products.c.productName,
                Products.c.categoryName,
                Products.c.description,
                Products.c.defaultImageUrl,
                Products.c.basePrice
            ).select_from(Products)
            
            # 카테고리 필터 적용
            if category and category.lower() != "show all":
                products_query = products_query.where(Products.c.categoryName == category)
            
            # 검색 필터 적용
            if search:
                products_query = products_query.where(
                    Products.c.productName.ilike(f"%{search}%")
                )
            
            # 제품 목록 조회
            products = db.execute(products_query.limit(limit)).fetchall()
            
            result_products = []
            
            for product in products:
                # 각 제품의 매장별 가격 정보 조회
                store_prices_query = select(
                    StoreOfferings.c.storeId,
                    StoreOfferings.c.price,
                    StoreOfferings.c.basePrice,
                    StoreOfferings.c.offerDetails,
                    Stores.c.storeName
                ).select_from(
                    StoreOfferings.join(Stores, StoreOfferings.c.storeId == Stores.c.storeId)
                ).where(StoreOfferings.c.productId == product.productId)
                
                # 특정 매장 필터 적용
                if store_id:
                    store_prices_query = store_prices_query.where(StoreOfferings.c.storeId == store_id)
                
                store_prices = db.execute(store_prices_query).fetchall()
                
                if not store_prices:
                    continue  # 매장별 가격이 없는 제품은 제외
                
                stores_info = []
                all_prices = []
                
                for store_price in store_prices:
                    final_price = float(store_price.price)
                    base_price = float(store_price.basePrice) if store_price.basePrice else final_price
                    
                    # 할인율 계산
                    discount_percentage = 0
                    if base_price > final_price:
                        discount_percentage = round(((base_price - final_price) / base_price) * 100)
                    
                    store_info = {
                        "store_id": store_price.storeId,
                        "store_name": store_price.storeName,
                        "original_price": base_price,
                        "final_price": final_price,
                        "discount_percentage": discount_percentage,
                        "savings": round(base_price - final_price, 2) if discount_percentage > 0 else 0,
                        "offer_details": store_price.offerDetails or "Regular Price",
                        "is_available": True
                    }
                    
                    stores_info.append(store_info)
                    all_prices.append(final_price)
                
                if not all_prices:
                    continue
                
                # 가격 필터 적용
                min_product_price = min(all_prices)
                max_product_price = max(all_prices)
                
                if min_price is not None and max_product_price < min_price:
                    continue
                if max_price is not None and min_product_price > max_price:
                    continue
                
                # 할인 필터 적용
                has_discount = any(s["discount_percentage"] > 0 for s in stores_info)
                if on_sale is not None:
                    if on_sale and not has_discount:
                        continue
                    if not on_sale and has_discount:
                        continue
                
                # 매장 필터가 적용되었는데 해당 매장 데이터가 없으면 제외
                if store_id and not any(s["store_id"] == store_id for s in stores_info):
                    continue
                
                # 가격 순으로 매장 정렬 (최저가 먼저)
                stores_info.sort(key=lambda x: x["final_price"])
                
                product_data = {
                    "productId": product.productId,
                    "productName": product.productName,
                    "categoryName": product.categoryName,
                    "description": product.description,
                    "defaultImageUrl": product.defaultImageUrl,
                    "basePrice": float(product.basePrice),
                    "stores": stores_info,
                    "lowest_price": min_product_price,
                    "highest_price": max_product_price,
                    "price_range": max_product_price - min_product_price,
                    "best_deal": stores_info[0] if stores_info else None,  # 최저가 매장
                    "has_discount": has_discount,
                    "total_stores": len(stores_info)
                }
                
                result_products.append(product_data)
            
            # 최저가 순으로 제품 정렬
            result_products.sort(key=lambda x: x["lowest_price"])
            
            return {
                "products": result_products,
                "total_count": len(result_products),
                "filters_applied": {
                    "category": category,
                    "search": search,
                    "store_id": store_id,
                    "min_price": min_price,
                    "max_price": max_price,
                    "on_sale": on_sale
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@router.get("/{product_id}", summary="Get specific product details")
def get_product_details(product_id: str) -> Dict[str, Any]:
    """특정 제품의 상세 정보 및 모든 매장별 가격 비교"""
    
    with SessionLocal() as db:
        try:
            # 제품 기본 정보 조회
            product_query = select(
                Products.c.productId,
                Products.c.productName,
                Products.c.categoryName,
                Products.c.description,
                Products.c.defaultImageUrl,
                Products.c.basePrice
            ).where(Products.c.productId == product_id)
            
            product = db.execute(product_query).fetchone()
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # 매장별 가격 정보 조회
            store_prices_query = select(
                StoreOfferings.c.storeId,
                StoreOfferings.c.price,
                StoreOfferings.c.basePrice,
                StoreOfferings.c.offerDetails,
                Stores.c.storeName
            ).select_from(
                StoreOfferings.join(Stores, StoreOfferings.c.storeId == Stores.c.storeId)
            ).where(StoreOfferings.c.productId == product_id)
            
            store_prices = db.execute(store_prices_query).fetchall()
            
            stores_info = []
            for store_price in store_prices:
                final_price = float(store_price.price)
                base_price = float(store_price.basePrice) if store_price.basePrice else final_price
                
                discount_percentage = 0
                if base_price > final_price:
                    discount_percentage = round(((base_price - final_price) / base_price) * 100)
                
                stores_info.append({
                    "store_id": store_price.storeId,
                    "store_name": store_price.storeName,
                    "original_price": base_price,
                    "final_price": final_price,
                    "discount_percentage": discount_percentage,
                    "savings": round(base_price - final_price, 2) if discount_percentage > 0 else 0,
                    "offer_details": store_price.offerDetails or "Regular Price"
                })
            
            # 가격 순 정렬
            stores_info.sort(key=lambda x: x["final_price"])
            
            # 가격 분석
            prices = [s["final_price"] for s in stores_info]
            price_analysis = {}
            
            if prices:
                price_analysis = {
                    "lowest_price": min(prices),
                    "highest_price": max(prices),
                    "average_price": round(sum(prices) / len(prices), 2),
                    "price_difference": max(prices) - min(prices),
                    "max_savings": max([s["savings"] for s in stores_info], default=0)
                }
            
            return {
                "product": {
                    "productId": product.productId,
                    "productName": product.productName,
                    "categoryName": product.categoryName,
                    "description": product.description,
                    "defaultImageUrl": product.defaultImageUrl,
                    "basePrice": float(product.basePrice)
                },
                "stores": stores_info,
                "price_analysis": price_analysis,
                "success": True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching product details: {str(e)}")

@router.get("/stores/", summary="Get all stores")
def get_stores() -> Dict[str, Any]:
    """모든 매장 목록 반환"""
    
    with SessionLocal() as db:
        try:
            stores_query = select(Stores.c.storeId, Stores.c.storeName)
            stores = db.execute(stores_query).fetchall()
            
            return {
                "stores": [
                    {"storeId": store.storeId, "storeName": store.storeName}
                    for store in stores
                ],
                "total_count": len(stores),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error fetching stores: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching stores: {str(e)}")

@router.get("/categories/", summary="Get all categories")
def get_categories() -> Dict[str, Any]:
    """모든 카테고리 목록 반환"""
    
    with SessionLocal() as db:
        try:
            categories_query = select(Products.c.categoryName).distinct()
            categories = db.execute(categories_query).fetchall()
            
            return {
                "categories": [
                    {"name": category.categoryName}
                    for category in categories if category.categoryName
                ],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.get("/health", summary="Health check")
def health_check():
    """API 상태 확인"""
    return {"status": "ok", "service": "products"}