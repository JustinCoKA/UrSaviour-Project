from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

router = APIRouter()

def get_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="yourpassword",  # Change this
            database="ursaviour"
        )
        return conn
    except Error as e:
        print("DB connection failed:", e)
        raise HTTPException(status_code=500, detail="Database connection failed")

class WatchlistItem(BaseModel):
    user_id: int
    product_id: int

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(item: WatchlistItem):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM watchlist WHERE user_id=%s AND product_id=%s",
        (item.user_id, item.product_id)
    )
    if cursor.fetchone():
        cursor.close(); conn.close()
        raise HTTPException(status_code=409, detail="Already in watchlist")

    cursor.execute(
        "INSERT INTO watchlist (user_id, product_id) VALUES (%s, %s)",
        (item.user_id, item.product_id)
    )
    conn.commit()
    cursor.close(); conn.close()
    return {"message": "Added to watchlist"}

@router.get("/{user_id}")
def get_watchlist(user_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM watchlist WHERE user_id=%s ORDER BY added_at DESC",
        (user_id,)
    )
    result = cursor.fetchall()
    cursor.close(); conn.close()
    return result

@router.delete("/{user_id}/{product_id}")
def remove_from_watchlist(user_id: int, product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM watchlist WHERE user_id=%s AND product_id=%s",
        (user_id, product_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    cursor.close(); conn.close()
    return {"message": "Removed successfully"}
Add Watchlist API route

