# backend/watchlist_routes.py
import os
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Session
from backend.db import Base, engine, get_db  # <-- adjust if your db file path differs

# ---------- MODEL ----------
class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uix_user_product"),)


# ---------- SCHEMAS ----------
class WatchlistCreate(BaseModel):
    user_id: int
    product_id: int

class WatchlistItem(BaseModel):
    id: int
    user_id: int
    product_id: int
    added_at: str
    class Config:
        orm_mode = True

class WatchlistDelete(BaseModel):
    user_id: int
    product_id: int


# ---------- ROUTER ----------
router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.post("/add", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)):
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == payload.user_id,
        Watchlist.product_id == payload.product_id
    ).first()
    if existing:
        return existing
    item = Watchlist(user_id=payload.user_id, product_id=payload.product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/view/{user_id}", response_model=List[WatchlistItem])
def view_watchlist(user_id: int, db: Session = Depends(get_db)):
    items = db.query(Watchlist).filter(Watchlist.user_id == user_id).order_by(Watchlist.added_at.desc()).all()
    return items

@router.delete("/remove", response_model=dict)
def remove_from_watchlist(payload: WatchlistDelete, db: Session = Depends(get_db)):
    item = db.query(Watchlist).filter(
        Watchlist.user_id == payload.user_id,
        Watchlist.product_id == payload.product_id
    ).first()
    if not item:
        return {"removed": False}
    db.delete(item)
    db.commit()
    return {"removed": True}
