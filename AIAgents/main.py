"""FastAPI app for the shopping agent.

POST /api/chat
- accepts JSON { "message": "...", "s3_bucket": "...", "s3_key": "..." }
- loads product CSV from S3 (if s3_bucket/s3_key provided or via env)
- formats product data into a text table
- combines user message + product data into COMPARE_PROMPT
- calls ask_openai and returns { "reply": text }

CORS origins may be configured with environment variable FRONTEND_ORIGINS
as a comma-separated list (if omitted, all origins are allowed).
"""
import os
from typing import Optional
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data_loader import load_csv_from_s3
from .openai_utils import ask_openai
from .prompts import COMPARE_PROMPT


class ChatRequest(BaseModel):
    message: str
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None


app = FastAPI()

# Configure simple logging for debug during local development
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS
_origins_env = os.getenv("FRONTEND_ORIGINS")
if _origins_env:
    ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    # If no explicit origins are set, allow all (useful for local development).
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Handle chat requests: combine user message with product data and call OpenAI.

    Request JSON example:
    {
      "message": "Help me pick the cheapest apple",
      "s3_bucket": "my-bucket",          # optional
      "s3_key": "path/to/products.csv"  # optional
    }
    """
    message = req.message

    # Resolve S3 location: request takes precedence, then environment variables
    bucket = req.s3_bucket or os.getenv("PRODUCT_S3_BUCKET")
    key = req.s3_key or os.getenv("PRODUCT_S3_KEY")

    product_table_text = ""
    if bucket and key:
        try:
            df = load_csv_from_s3(bucket, key)
            # Convert DataFrame to a compact text table. to_string works reliably
            # without extra dependencies.
            product_table_text = df.to_string(index=False)
        except FileNotFoundError:
            # If the file isn't found, proceed without product data.
            product_table_text = ""
            logger.info("Product data not found at s3://%s/%s; continuing without product data", bucket, key)
        except Exception as e:
            # Unexpected S3 / parsing errors should return a 500 to the client.
            logger.exception("Error loading product data from s3://%s/%s", bucket, key)
            raise HTTPException(status_code=500, detail=f"Error loading product data: {e}")

    if not product_table_text:
        product_table_text = "No product data found."

    prompt = COMPARE_PROMPT.format(user_message=message, product_data=product_table_text)

    try:
        reply = ask_openai(prompt)
    except Exception as e:
        # Log full traceback to server logs for diagnosis, but return a concise error to clients.
        logger.exception("OpenAI request failed")
        raise HTTPException(status_code=500, detail=f"OpenAI request failed: {e}")

    return {"reply": reply}


@app.get("/api/v1/products/")
def get_products_sample():
    """Lightweight sample products endpoint for local development.

    Returns a small list of products in the shape expected by the frontend
    so developers can work without a real product API or S3 backend.
    """
    sample = {
        "products": [
            {
                "id": "P001",
                "name": "Acme Extra Virgin Olive Oil 500ml",
                "category": "Pantry",
                "description": "Cold-pressed extra virgin olive oil.",
                "image": "https://via.placeholder.com/320x240?text=Olive+Oil",
                "special": None,
                "stores": [
                    {"brand": "ShopA", "price": 9.99, "original_price": 12.99},
                    {"brand": "ShopB", "price": 10.49}
                ]
            },
            {
                "id": "P002",
                "name": "Farm Fresh Eggs (12)",
                "category": "Dairy",
                "description": "Free-range large eggs, dozen pack.",
                "image": "https://via.placeholder.com/320x240?text=Eggs",
                "special": {"type": "discount", "note": "10% off"},
                "stores": [
                    {"brand": "MarketX", "price": 4.49, "original_price": 4.99}
                ]
            }
        ]
    }

    return sample
