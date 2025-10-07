# backend/app/api/v1/endpoints/products.py
from fastapi import APIRouter, Query
from sqlalchemy import select, func, desc, MetaData, Table
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter()

# Reflect tables (use existing schema names)
metadata = MetaData()
Products       = Table("products",           metadata, autoload_with=engine)
ProductCats    = Table("productCategories",  metadata, autoload_with=engine)
StoreOfferings = Table("storeOfferings",     metadata, autoload_with=engine)
Stores         = Table("stores",             metadata, autoload_with=engine)

def _col(t, name): 
    return getattr(t.c, name, None)

def _maybe(col_obj, label=None):
    if col_obj is None:
        return None
    return col_obj.label(label) if label else col_obj

def _latest_week(db: Session):
    week_col = _col(StoreOfferings, "week")
    if week_col is None:
        return None
    return db.execute(select(func.max(week_col))).scalar()

@router.get("/products")
def list_products(q: str | None = Query(None), limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Return products in the format expected by frontend: array of products with stores"""
    with SessionLocal() as db:
        # Get all products - use actual column names from the database
        product_cols = [
            _maybe(_col(Products, "productId"), "id"),
            _maybe(_col(Products, "productName"), "name"),
            _maybe(_col(Products, "description")),
            _maybe(_col(Products, "defaultImageUrl"), "image"),
            _maybe(_col(Products, "basePrice"), "base_price"),
            _maybe(_col(Products, "categoryName"), "category")
        ]
        product_cols = [c for c in product_cols if c is not None]

        # Base query for products
        product_sel = select(*product_cols).select_from(Products)
        
        if q and _col(Products, "productName") is not None:
            product_sel = product_sel.where(_col(Products, "productName").ilike(f"%{q}%"))
        
        product_sel = product_sel.limit(limit).offset(offset)
        products = db.execute(product_sel).mappings().all()

        # Get all stores for the store list - use actual column names
        store_sel = select(
            _maybe(_col(Stores, "storeId"), "store_id"),
            _maybe(_col(Stores, "storeName"), "brand")
        ).select_from(Stores)
        stores = {row.store_id: row.brand for row in db.execute(store_sel).mappings().all()}

        # Transform to frontend format
        result = []
        for product in products:
            # Convert product to dict
            product_dict = dict(product)
            
            # Create stores array - use base_price for all stores if no offerings exist
            base_price = product_dict.get("base_price", 10.0)  # fallback price
            stores_list = []
            for store_id, brand in stores.items():
                stores_list.append({
                    "brand": brand,
                    "price": float(base_price)
                })
            
            # Format the product for frontend
            formatted_product = {
                "id": product_dict.get("id", ""),
                "name": product_dict.get("name", ""),
                "category": product_dict.get("category", ""),
                "description": product_dict.get("description", ""),
                "image": product_dict.get("image", f"/images/p/{product_dict.get('id', 'default')}.jpg"),
                "stores": stores_list
            }
            result.append(formatted_product)

        return result

@router.get("/products/{product_id}")
def get_product(product_id: int):
    with SessionLocal() as db:
        week = _latest_week(db)
        sel = (
            select(
                _maybe(_col(Products, "id"), "product_id"),
                _maybe(_col(Products, "sku")),
                _maybe(_col(Products, "name")),
                _maybe(_col(Products, "description")),
                _maybe(_col(Products, "image_url")),
                _maybe(_col(ProductCats, "name"), "category"),
                _maybe(_col(StoreOfferings, "price_regular")),
                _maybe(_col(StoreOfferings, "price_special")),
                _maybe(_col(StoreOfferings, "discount_rate")),
            )
            .select_from(
                Products.outerjoin(ProductCats, _col(Products, "category_id") == _col(ProductCats, "id"))
                        .outerjoin(StoreOfferings, _col(StoreOfferings, "product_id") == _col(Products, "id"))
            )
            .where((_col(Products, "id") == product_id) & (_col(StoreOfferings, "week") == week))
        )
        row = db.execute(sel).mappings().first()
        return {"week": week, "item": row}
    

