# backend/app/api/v1/endpoints/assistant.py
# AI Assistant using backend database data for price comparison across 4 stores
import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, MetaData, Table, or_
from openai import OpenAI

from app.core.config import settings
from app.db.session import ProductsSessionLocal, products_engine

logger = logging.getLogger(__name__)
router = APIRouter()

# === CONFIGURABLE SYSTEM PROMPT ===
# Modify this prompt to change AI assistant behavior
SYSTEM_PROMPT = """You are a helpful price comparison assistant for UrSaviour grocery platform.

Your PRIMARY goal: Help users find the cheapest prices across our 4 stores (Justin Groceries, Mio Mart, Austin Fresh, Aadarsh Deals).

IMPORTANT RULES:
1. ONLY use the product data provided in the context - NEVER make up prices or products
2. When comparing prices, show ALL 4 stores with their prices
3. Clearly highlight which store has the CHEAPEST price
4. If a product isn't in the data, say "I don't have price information for that product"
5. Keep responses concise (under 200 words)
6. Format price comparisons as a clear list
7. If user asks for recipes or meal ideas, suggest meals based on products available in the provided data ONLY.
8. If the user askes for nutritional information, only provide details if they are included in the provided data. Do not fabricate any nutritional facts.
9. If user askes for help with techinical issues regarding the login or signup issues, direct them to contact support at admin@admin.com and appologize for the inconvenience.
10. If the user asks for the ingredients for recipe, Please list all the ingredients with the cheapest prices for each ingredient, NO need to compare prices in this case. 
11. IF the product is not found in any of the 4 stores, respond with "We could not find that product in any of our stores. Do you want to finnd anything else?"
12. If possile, suggest the user with a different product to hook the user to use the chat.

Example response format:    
"Here are the milk prices across our stores:
- Justin Groceries: $3.50
- Mio Mart: $3.45 ✓ CHEAPEST
- Austin Fresh: $3.60
- Aadarsh Deals: $3.55

The best deal is at Mio Mart for $3.45!"
"""

# === OpenAI Setup ===
try:
    # Try to get from settings first (reads from root .env via config.py)
    openai_key = None
    if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
        # OPENAI_API_KEY is a SecretStr, need to extract the actual value
        openai_key = settings.OPENAI_API_KEY.get_secret_value()
    
    # Fallback to direct environment variable
    if not openai_key:
        openai_key = os.getenv("OPENAI_API_KEY")
    
    client = OpenAI(api_key=openai_key) if openai_key else None
    
    if not client:
        logger.warning("⚠️ OpenAI API key not configured - check .env file")
    else:
        logger.info("✅ OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# === Database Tables ===
metadata = MetaData()
_tables_initialized = False
Products = Stores = StoreOfferings = StoreBasePrices = None

def _ensure_tables():
    """Lazy load database tables"""
    global _tables_initialized, Products, Stores, StoreOfferings, StoreBasePrices
    if not _tables_initialized:
        try:
            Products = Table("products", metadata, autoload_with=products_engine)
            Stores = Table("stores", metadata, autoload_with=products_engine)
            StoreOfferings = Table("storeOfferings", metadata, autoload_with=products_engine)
            StoreBasePrices = Table("store_base_prices", metadata, autoload_with=products_engine)
            _tables_initialized = True
            logger.info("✅ Database tables loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load database tables: {e}")

# === Request/Response Models ===
class ChatRequest(BaseModel):
    message: str
    userId: Optional[str] = None
    conversationId: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    conversationId: Optional[str] = None

# === Core Functions ===
def get_product_context_from_db(search_query: str) -> str:
    """
    Query backend database for product price information across all stores.
    Returns formatted text with actual product data for AI context.
    """
    try:
        _ensure_tables()
        with ProductsSessionLocal() as db:
            # Extract key search terms (split on spaces, take meaningful words)
            search_terms = [term.strip().lower() for term in search_query.split() if len(term.strip()) > 2]
            
            # If no good search terms, get all products (limit 20)
            if not search_terms:
                products_query = select(
                    Products.c.productId,
                    Products.c.productName,
                    Products.c.categoryName,
                    Products.c.basePrice
                ).limit(20)
            else:
                # Search for products matching ANY of the terms in name or category
                search_conditions = []
                for term in search_terms:
                    search_conditions.append(Products.c.productName.ilike(f"%{term}%"))
                    search_conditions.append(Products.c.categoryName.ilike(f"%{term}%"))
                
                products_query = select(
                    Products.c.productId,
                    Products.c.productName,
                    Products.c.categoryName,
                    Products.c.basePrice
                ).where(or_(*search_conditions)).limit(20)
            
            products = db.execute(products_query).fetchall()
            
            if not products:
                # If still no results, get top 10 products from database
                products_query = select(
                    Products.c.productId,
                    Products.c.productName,
                    Products.c.categoryName,
                    Products.c.basePrice
                ).limit(10)
                products = db.execute(products_query).fetchall()
                
                if not products:
                    return "Database appears to be empty. No products available."
            
            # Build context with store prices for each product
            context_parts = []
            
            for product in products:
                product_info = [
                    f"\n=== {product.productName} ===",
                    f"Category: {product.categoryName}",
                    f"Product ID: {product.productId}",
                    "\nPrices by Store:"
                ]
                
                # Get store-specific base prices
                base_prices_query = select(
                    StoreBasePrices.c.storeId,
                    StoreBasePrices.c.basePrice
                ).where(StoreBasePrices.c.productId == product.productId)
                
                base_prices = db.execute(base_prices_query).fetchall()
                
                # Get store names
                stores_query = select(Stores.c.storeId, Stores.c.storeName)
                stores = db.execute(stores_query).fetchall()
                stores_dict = {s.storeId: s.storeName for s in stores}
                
                # Get special offerings (discounts)
                offerings_query = select(
                    StoreOfferings.c.storeId,
                    StoreOfferings.c.price,
                    StoreOfferings.c.basePrice,
                    StoreOfferings.c.offerDetails
                ).where(StoreOfferings.c.productId == product.productId)
                
                offerings = db.execute(offerings_query).fetchall()
                offerings_dict = {o.storeId: o for o in offerings}
                
                # Compile prices for all stores
                for store_id, store_name in stores_dict.items():
                    # Check if there's a special offer
                    if store_id in offerings_dict:
                        offer = offerings_dict[store_id]
                        price = offer.price if offer.price else offer.basePrice
                        offer_text = f" ({offer.offerDetails})" if offer.offerDetails else ""
                        product_info.append(f"  • {store_name}: ${price:.2f}{offer_text}")
                    else:
                        # Use base price
                        base_price = next((bp.basePrice for bp in base_prices if bp.storeId == store_id), product.basePrice)
                        if base_price:
                            product_info.append(f"  • {store_name}: ${float(base_price):.2f}")
                
                context_parts.append("\n".join(product_info))
            
            result = "\n".join(context_parts)
            logger.info(f"Found {len(products)} products for query: {search_query}")
            return result
            
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return f"Error retrieving product data: {str(e)}"

@router.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "ai_assistant"}

@router.get("/test")
def test():
    """Test endpoint to verify assistant is working"""
    return {
        "status": "ok",
        "openai_configured": client is not None,
        "database_available": _tables_initialized or products_engine is not None,
        "system_prompt_preview": SYSTEM_PROMPT[:100] + "..."
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - compares product prices using ONLY backend database data
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")
    
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI not configured. Please set OPENAI_API_KEY in .env")
    
    try:
        # Get real product data from backend database
        product_context = get_product_context_from_db(request.message)
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context (REAL DATA FROM DATABASE):\n{product_context}\n\nUser Question: {request.message}"}
        ]
        
        # Get AI response using real data
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.3  # Lower temperature = more factual, less creative
        )
        
        answer = response.choices[0].message.content
        
        logger.info(f"Chat processed - User: {request.userId}, Query: {request.message[:50]}...")
        
        return ChatResponse(
            answer=answer,
            conversationId=request.conversationId
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")

# Initialize tables on module load
_ensure_tables()


