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

@router.get("", summary="List Products")
def list_products(q: str | None = Query(None), limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
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
        stores = {row["store_id"]: row["brand"] for row in db.execute(store_sel).mappings().all()}

        # Filter to exactly 4 main stores (matching frontend expectations)
        main_store_names = ["Justin Groceries", "Mio Mart", "Austin Fresh", "Aadarsh Deals"]
        main_stores = {sid: name for sid, name in stores.items() if name in main_store_names}
        
        # If we don't have exactly 4 stores, use what we have but limit to 4
        if len(main_stores) != 4:
            main_stores = dict(list(stores.items())[:4])

        # Get store offerings with discounts - use actual column names
        offerings_data = {}
        if _col(StoreOfferings, "productId") is not None and _col(StoreOfferings, "storeId") is not None:
            offerings_sel = select(
                _maybe(_col(StoreOfferings, "productId"), "product_id"),
                _maybe(_col(StoreOfferings, "storeId"), "store_id"),
                _maybe(_col(StoreOfferings, "basePrice"), "base_price"),
                _maybe(_col(StoreOfferings, "price"), "price"),
                _maybe(_col(StoreOfferings, "offerDetails"), "offer_details")
            ).select_from(StoreOfferings)
            offerings_cols = [c for c in offerings_sel.selected_columns if c is not None]

            if offerings_cols:
                for row in db.execute(select(*offerings_cols)).mappings().all():
                    # Normalize keys and ensure numeric casting
                    pid = row.get("product_id")
                    sid = row.get("store_id")
                    key = (str(pid), str(sid))
                    offerings_data[key] = {
                        "product_id": pid,
                        "store_id": sid,
                        "base_price": float(row.get("base_price") or 0.0),
                        "price": float(row.get("price") or 0.0),
                        "offer_details": row.get("offer_details")
                    }

        # Transform to frontend format
        result = []
        for product in products:
            product_dict = dict(product)
            product_id = product_dict.get("id")
            
            # Create stores array with proper pricing and discounts
            stores_list = []
            for store_id, brand in main_stores.items():
                # Get base price from product (product may have base_price column)
                base_price = float(product_dict.get("base_price") or 0.0)

                offering = offerings_data.get((product_id, str(store_id)))

                if offering and offering.get("price") and offering.get("price") > 0:
                    original_price = offering.get("base_price") or base_price or None
                    discounted_price = offering.get("price")
                    offer_type = offering.get("offer_details") or None

                    store_data = {
                        "brand": brand,
                        "price": float(discounted_price),
                        "original_price": float(original_price) if original_price else None
                    }

                    if offer_type and "special" not in product_dict:
                        product_dict["special"] = {"type": offer_type, "store": brand}
                else:
                    # No offering: fall back to product base_price or small variation
                    if base_price > 0:
                        varied_price = base_price
                    else:
                        # fallback nominal price to avoid NaN
                        varied_price = 9.99
                    store_data = {"brand": brand, "price": float(varied_price), "original_price": None}

                stores_list.append(store_data)
            
            # Format the product for frontend
            formatted_product = {
                "id": product_dict.get("id", ""),
                "name": product_dict.get("name", ""),
                "category": product_dict.get("category", ""),
                "description": product_dict.get("description", ""),
                "image": product_dict.get("image", f"/images/p/{product_dict.get('id', 'default')}.jpg"),
                "stores": stores_list
            }
            
            # Add special offer info if present
            if "special" in product_dict:
                formatted_product["special"] = product_dict["special"]
            
            result.append(formatted_product)

        return result

@router.get("/{product_id}", summary="Get Product")
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
    

