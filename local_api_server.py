#!/usr/bin/env python3
"""
Simple local development API server for UrSaviour
This provides mock data to test the frontend without setting up a full database
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI(title="UrSaviour Local Dev API", version="1.0.0")

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock product data
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Fresh Bananas",
        "price": 2.99,
        "description": "Fresh organic bananas from local farms",
        "category": "Fruit",
        "image_url": "/images/banana.jpg",
        "special": {"type": "10% OFF", "store": "Fresh Market"},
        "in_stock": True
    },
    {
        "id": 2,
        "name": "Whole Milk",
        "price": 4.50,
        "description": "Fresh whole milk 1L",
        "category": "Dairy",
        "image_url": "/images/milk.jpg",
        "special": {"type": "Half Price", "store": "Super Store"},
        "in_stock": True
    },
    {
        "id": 3,
        "name": "Bread Loaf",
        "price": 3.20,
        "description": "Fresh baked white bread",
        "category": "Bakery",
        "image_url": "/images/bread.jpg",
        "special": None,
        "in_stock": True
    },
    {
        "id": 4,
        "name": "Ground Coffee",
        "price": 8.99,
        "description": "Premium ground coffee 500g",
        "category": "Beverages",
        "image_url": "/images/coffee.jpg",
        "special": {"type": "30% OFF", "store": "Coffee World"},
        "in_stock": True
    },
    {
        "id": 5,
        "name": "Chicken Breast",
        "price": 12.50,
        "description": "Fresh chicken breast 1kg",
        "category": "Meat",
        "image_url": "/images/chicken.jpg",
        "special": {"type": "Big deal", "store": "Meat House"},
        "in_stock": True
    }
]

@app.get("/")
def root():
    return {"message": "UrSaviour Local Development API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/products/products")
def get_products(limit: int = 100) -> Dict[str, Any]:
    """Get products with pagination support"""
    products_to_return = MOCK_PRODUCTS[:limit] if limit < len(MOCK_PRODUCTS) else MOCK_PRODUCTS
    
    return {
        "products": products_to_return,
        "total": len(MOCK_PRODUCTS),
        "limit": limit,
        "offset": 0
    }

@app.get("/api/v1/products/search")
def search_products(q: str = "", category: str = "", limit: int = 100) -> Dict[str, Any]:
    """Search products by name or category"""
    filtered_products = MOCK_PRODUCTS
    
    if q:
        filtered_products = [p for p in filtered_products if q.lower() in p["name"].lower() or q.lower() in p["description"].lower()]
    
    if category and category.lower() != "all":
        filtered_products = [p for p in filtered_products if category.lower() == p["category"].lower()]
    
    products_to_return = filtered_products[:limit] if limit < len(filtered_products) else filtered_products
    
    return {
        "products": products_to_return,
        "total": len(filtered_products),
        "limit": limit,
        "offset": 0,
        "query": q,
        "category": category
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)