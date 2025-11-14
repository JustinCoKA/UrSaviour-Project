import os
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, MetaData, Table, or_
from openai import OpenAI
from datetime import datetime
from sqlalchemy import insert

from app.core.config import settings
from app.db.session import ProductsSessionLocal, products_engine

logger = logging.getLogger(__name__)
router = APIRouter()

#Openai setting to access the key in the .env outside the backend
#openapi_key = os.getenv("OPENAI_API_KEY")  
try:
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if openai_key:
        openai_key = openai_key.get_secret_value()
    else:
        openai_key = os.getenv("OPENAI_API_KEY")
    
    client = OpenAI(api_key=openai_key) if openai_key else None
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

#promt to set the ai function, behaviourr
the_aipromt = """You are a helpful price comparison assistant for UrSaviour grocery platform.

Your job: Help users find cheapest prices across our 4 stores (Justin Groceries, Mio Mart, Austin Fresh, Aadarsh Deals).

RULES:
ONLY use the product data provided in the context - NEVER make up prices or products
When comparing prices, show ALL 4 stores with their prices
Clearly highlight which store has the CHEAPEST price
If a product isn't in the data, say "I don't have price information for that product"
Keep responses concise (under 200 words)
Format price comparisons as a clear list
If user asks for recipes or meal ideas, suggest meals based on products available in the provided data ONLY.
If the user asks for nutritional information, only provide details if they are included in the provided data. Do not fabricate any nutritional facts.
For issue relating to technical issue like login or sign, provide email support at admin@admin.com and apologize for the inconvenience.
If the user asks for the ingredients for a recipe, please list all the ingredients with the cheapest prices for each ingredient, NO need to compare prices in this case. 
If the product is not found in any of the 4 stores, respond with "We could not find that product in any of our stores. Do you want to find anything else?"
If possible, suggest the user a different product to hook the user to use the chat.
If the cheapest price and 2 stores offer the same cheapest price, highlight both stores as CHEAPEST.
If user asks a product that have a same name, then list and ask which one they mean.

Example format for response:    
"Here are the milk prices across our stores:
- Justin Groceries: $3.50
- Mio Mart: $3.45 ✓ CHEAPEST
- Austin Fresh: $3.60
- Aadarsh Deals: $3.55

The best deal is at Mio Mart for $3.45!"
"""


metadata = MetaData()
Products = Stores = StoreOfferings = StoreBasePrices = ConversationHistory = None
#Take the tables from the mysql wokbench 
def _ensure_tables():
    global Products, Stores, StoreOfferings, StoreBasePrices, ConversationHistory
    if Products is None:
        Products = Table("products", metadata, autoload_with=products_engine)
        Stores = Table("stores", metadata, autoload_with=products_engine)
        StoreOfferings = Table("storeOfferings", metadata, autoload_with=products_engine)
        StoreBasePrices = Table("store_base_prices", metadata, autoload_with=products_engine)  
        ConversationHistory = Table("save_conversation_history", metadata, autoload_with=products_engine)

class ChatRequest(BaseModel):
    message: str
    userId: Optional[str] = None
    conversationId: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    conversationId: Optional[str] = None

def get_product_context_from_db(search_query: str) -> str:
    _ensure_tables()
    with ProductsSessionLocal() as db:
        conds = []  # search conditions
        for term in search_query.split():
            if len(term.strip()) > 2:  
                term = term.strip().lower()
                conds.append(Products.c.productName.ilike(f"%{term}%"))
                conds.append(Products.c.categoryName.ilike(f"%{term}%"))
        
       
        q = select(
            Products.c.productId,
            Products.c.productName,
            Products.c.categoryName,
            Products.c.basePrice
        )
        if conds:
            q = q.where(or_(*conds))
        
        products = db.execute(q.limit(20)).fetchall()
        parts = []
        #debug only 
        for product in products:
            info = [
                f"\n=== {product.productName} ===",
                f"Category: {product.categoryName}",
                f"Product ID: {product.productId}",
                "\nPrices by Store:"
            ]
            
            bp_query = select(
                StoreBasePrices.c.storeId,
                StoreBasePrices.c.basePrice
            ).where(StoreBasePrices.c.productId == product.productId)
            
            base_prices = db.execute(bp_query).fetchall()
            # grabbing all stores 
            stores = db.execute(select(Stores.c.storeId, Stores.c.storeName)).fetchall()
            store_map = {s.storeId: s.storeName for s in stores}
            
            offers_q = select(
                StoreOfferings.c.storeId,
                StoreOfferings.c.price,
                StoreOfferings.c.basePrice,
                StoreOfferings.c.offerDetails
            ).where(StoreOfferings.c.productId == product.productId)
            
            offers = db.execute(offers_q).fetchall()
            offer_map = {o.storeId: o for o in offers}
            
            for sid, sname in store_map.items():
                if sid in offer_map:
                    off = offer_map[sid]
                    price = off.price if off.price else off.basePrice
                    offer_text = f" ({off.offerDetails})" if off.offerDetails else ""
                    info.append(f"  • {sname}: ${price:.2f}{offer_text}")
                else:
                    bp = next((b.basePrice for b in base_prices if b.storeId == sid), product.basePrice)
                    if bp:
                        info.append(f"  • {sname}: ${float(bp):.2f}")
            
            parts.append("\n".join(info))
        
        result = "\n".join(parts)
        return result
#save function for chat conversation
def save_conversation_message(conversation_id: str, user_id: Optional[str], role: str, message: str):
    _ensure_tables()
    with ProductsSessionLocal() as db:
        
        stmt = insert(ConversationHistory).values(
            conversationId=conversation_id,
            userId=user_id,
            role=role,
            message=message,
            timestamp=datetime.now()
        )
        db.execute(stmt)
        db.commit()


@router.get("/health")
def health():
    return {"status": "ok", "service": "ai_assistant"}

@router.get("/test")
def test():
    # for test to see if it is loaded or not
    return {
        "status": "ok",
        "openai_configured": client is not None,
        "database_available": _tables_initialized or products_engine is not None,
        "system_prompt_preview": the_aipromt [:100] + "..."
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")
    
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI not configured")
    
    try:
        if not request.conversationId:
            import uuid
            request.conversationId = str(uuid.uuid4())
        # debugging
        product_context = get_product_context_from_db(request.message)
        
        messages = [{"role": "system", "content": the_aipromt}]
        messages.append({"role": "user", "content": f"Context (REAL DATA FROM DATABASE):\n{product_context}\n\nUser Question: {request.message}"})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.3  
        )
        
        answer = response.choices[0].message.content
        
        # save both messages
        save_conversation_message(request.conversationId, request.userId, "user", request.message)
        save_conversation_message(request.conversationId, request.userId, "assistant", answer)
        
        user_type = "logged-in user" if request.userId else "guest"
        logger.info(f"Chat saved for {user_type}: {request.userId or 'no userId'}")
        
        logger.info(f"Chat processed - User: {request.userId or 'guest'}, Query: {request.message[:50]}...")
        
        return ChatResponse(
            answer=answer,
            conversationId=request.conversationId
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")

_ensure_tables()
