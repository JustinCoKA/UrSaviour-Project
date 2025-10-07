# backend/app/api/v1/endpoints/products.py
from fastapi import APIRouter, Query
from sqlalchemy import select, func, desc, MetaData, Table
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from datetime import datetime

router = APIRouter()

# Reflect tables (use existing schema names)
metadata = MetaData()
Products       = Table("products",           metadata, autoload_with=engine)
ProductCats    = Table("productCategories",  metadata, autoload_with=engine)
StoreOfferings = Table("storeOfferings",     metadata, autoload_with=engine)

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
def list_products(q: str | None = Query(None), limit: int = 50, offset: int = 0):
    with SessionLocal() as db:
        week = _latest_week(db)
        # Build select list only including columns that exist in the reflected tables
        cols = []
        cols.append(_maybe(_col(Products, "id"), "product_id"))
        cols.append(_maybe(_col(Products, "sku")))
        cols.append(_maybe(_col(Products, "name")))
        cols.append(_maybe(_col(Products, "description")))
        cols.append(_maybe(_col(Products, "image_url")))
        cols.append(_maybe(_col(ProductCats, "name"), "category"))
        cols.append(_maybe(_col(StoreOfferings, "price_regular")))
        cols.append(_maybe(_col(StoreOfferings, "price_special")))
        cols.append(_maybe(_col(StoreOfferings, "discount_rate")))

        # Filter out missing columns
        cols = [c for c in cols if c is not None]

        # If key columns are missing (e.g. Products.id or StoreOfferings.week), return empty result
        if not _col(Products, "id") or not _col(StoreOfferings, "week"):
            return {"week": week, "items": []}

        # Build base select and joins only when join cols exist
        sel = select(*cols).select_from(Products)
        if _col(Products, "category_id") is not None and _col(ProductCats, "id") is not None:
            sel = sel.outerjoin(ProductCats, _col(Products, "category_id") == _col(ProductCats, "id"))
        if _col(StoreOfferings, "product_id") is not None and _col(Products, "id") is not None:
            sel = sel.outerjoin(StoreOfferings, _col(StoreOfferings, "product_id") == _col(Products, "id"))

        if week is not None:
            sel = sel.where(_col(StoreOfferings, "week") == week)

        if _col(StoreOfferings, "discount_rate") is not None:
            sel = sel.order_by(desc(_col(StoreOfferings, "discount_rate")))

        sel = sel.limit(limit).offset(offset)

        if q and _col(Products, "name") is not None:
            sel = sel.where(_col(Products, "name").ilike(f"%{q}%"))

        rows = db.execute(sel).mappings().all()
        return {"week": week, "items": rows}

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
    

