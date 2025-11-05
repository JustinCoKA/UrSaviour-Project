# backend/routers/watchlist.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import mysql.connector

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"]
)

# 1) change these to your actual DB settings
def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="ursaviour"   # <- change to your db
    )
    return conn

class WatchlistItemIn(BaseModel):
    user_id: int
    product_id: int

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(item: WatchlistItemIn):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # check if exists
    cursor.execute(
        "SELECT id FROM watchlist WHERE user_id=%s AND product_id=%s",
        (item.user_id, item.product_id)
    )
    exists = cursor.fetchone()
    if exists:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already in watchlist"
        )

    cursor.execute(
        "INSERT INTO watchlist (user_id, product_id) VALUES (%s, %s)",
        (item.user_id, item.product_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, "message": "added to watchlist"}

@router.get("/{user_id}")
def get_watchlist(user_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # if you have a products table join it here
    cursor.execute("""
        SELECT w.id, w.product_id, w.added_at
        FROM watchlist w
        WHERE w.user_id = %s
        ORDER BY w.added_at DESC
    """, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

@router.delete("/{user_id}/{product_id}")
def remove_from_watchlist(user_id: int, product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM watchlist WHERE user_id=%s AND product_id=%s",
        (user_id, product_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Not found in watchlist")

    return {"message": "removed"}

