# app.py
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import boto3
import pandas as pd
import PyPDF2
from io import BytesIO, StringIO
import chromadb

load_dotenv()
import logging

# Configure module logger. Default to WARNING to reduce console noise in dev.
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("AILucky")

# --- Setup ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="Simple AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://www.ursaviour.com/Chat-page.html"],  # allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve frontend static/templates directory relative to this file so
# running uvicorn from other working directories won't break mounting.
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "frontend", "src")
if not os.path.isdir(static_dir):
    # create the directory to avoid startup runtime errors when static/templates
    # are missing (keeps dev experience smooth). If you prefer an explicit
    # error instead, remove this block.
    logger.warning(f"⚠️ Static/templates directory '{static_dir}' not found — creating it.")
    os.makedirs(static_dir, exist_ok=True)

app.mount("/frontend", StaticFiles(directory="frontend/src"), name="frontend")
templates = Jinja2Templates(directory="frontend/src")

# --- S3 setup ---
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")
)
BUCKET = os.getenv("BUCKET_NAME")

# --- Chroma setup ---
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection("simple_rag")

# --- Helpers ---
def get_embedding(text):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding

def get_tone_prompt(tone):
    prompts = {
        "default": "You are a clear and helpful assistant.",
        "friendly": "You are friendly, casual, and easy to understand.",
        "technical": "You are a technical expert. Use precise and factual tone.",
        "teacher": "You explain things clearly and step-by-step like a teacher."
    }
    return prompts.get(tone, prompts["default"])

def read_csv_from_s3(bucket, key):
    data = s3.get_object(Bucket=bucket, Key=key)
    body = data.get("Body")
    if body is None:
        logger.warning(f"⚠️ S3 object {key} has no Body")
        return ""
    raw = body.read()
    if not raw:
        logger.warning(f"⚠️ S3 object {key} is empty")
        return ""
    try:
        content = raw.decode("utf-8")
    except Exception:
        # Fallback to latin-1/ignore to avoid crashes on unexpected encodings
        try:
            content = raw.decode("latin-1")
        except Exception as e:
            logger.warning(f"⚠️ Could not decode CSV {key}: {e}")
            return ""
    try:
        df = pd.read_csv(StringIO(content))
        return "\n".join(df.astype(str).apply(" ".join, axis=1).tolist())
    except Exception as e:
        # If parsing fails, return the raw content as a fallback so we can still
        # create embeddings from the text rather than crashing the startup.
        logger.warning(f"⚠️ Failed to parse CSV {key}: {e}; returning raw content as fallback")
        return content or ""

def read_pdf_from_s3(bucket, key):
    data = s3.get_object(Bucket=bucket, Key=key)
    body = data.get("Body")
    if body is None:
        logger.warning(f"⚠️ S3 object {key} has no Body")
        return ""
    raw = body.read()
    if not raw:
        logger.warning(f"⚠️ S3 object {key} is empty")
        return ""
    try:
        reader = PyPDF2.PdfReader(BytesIO(raw))
    except Exception as e:
        logger.warning(f"⚠️ Could not read PDF {key}: {e}")
        return ""
    texts = []
    for page in reader.pages:
        try:
            t = page.extract_text()
            if t:
                texts.append(t)
        except Exception:
            # ignore page-level extraction failures
            continue
    return "\n".join(texts)

def load_data_from_s3():
    if not BUCKET:
        logger.warning("⚠️ BUCKET_NAME not set; skipping S3 data load")
        return
    resp = s3.list_objects_v2(Bucket=BUCKET)
    files = resp.get("Contents", []) if resp else []
    logger.info(f"📦 Found {len(files)} files in {BUCKET}")
    for f in files:
        key = f.get("Key")
        if not key:
            continue

        if key.endswith(".csv"):
            text = read_csv_from_s3(BUCKET, key)
        elif key.endswith(".pdf"):
            text = read_pdf_from_s3(BUCKET, key)
        else:
            logger.warning(f"⚪ Skipping unsupported file type: {key}")
            continue

        if not text:
            logger.warning(f"⚠️ Skipping {key}: no text extracted")
            continue

        try:
            emb = get_embedding(text[:2000])  # limit size
        except Exception as e:
            logger.warning(f"⚠️ Failed to create embedding for {key}: {e}")
            continue

        try:
            collection.add(documents=[text[:2000]], embeddings=[emb], ids=[key])
        except Exception as e:
            logger.warning(f"⚠️ Failed to add {key} to Chroma collection: {e}")

    logger.info("✅ Data loaded into Chroma")

# --- Routes ---
@app.on_event("startup")
def startup_event():
    try:
        load_data_from_s3()
    except Exception as e:
        logger.warning("⚠️ Could not load data: %s", e)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("Chat-page.html", {"request": request})

@app.get("/api/v1/products/")
async def get_products():
    """
    Simulated endpoint to retrieve product data for the main UI.
    In a full project, this would query your primary database (e.g., MySQL).
    """
    # NOTE: Since you don't have a database connection setup here, 
    # we'll return a sample of structured data that your frontend expects.
    
    # These samples reflect your project's goal of price comparison and savings.
    sample_products = [
        {
            "id": 101,
            "name": "Milk (2L Full Cream)",
            "store": "Coles",
            "price": 3.40,
            "best_price": 3.15,
            "savings_potential": 0.25,
            "unit_price": "1.70 / L"
        },
        {
            "id": 102,
            "name": "Eggs (Dozen, Free Range)",
            "store": "Woolworths",
            "price": 6.80,
            "best_price": 6.50,
            "savings_potential": 0.30,
            "unit_price": "0.57 / egg"
        },
        {
            "id": 103,
            "name": "Pasta (500g Spaghetti)",
            "store": "Aldi",
            "price": 1.15,
            "best_price": 1.15,
            "savings_potential": 0.00,
            "unit_price": "0.23 / 100g"
        },
    ]

    return {"products": sample_products}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    question = body.get("message", "")
    tone = body.get("tone", "default")

    if not question:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    q_emb = get_embedding(question)
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    context = "\n\n".join(results["documents"][0]) if results["documents"] else "No context found."

    logger.debug("%s", "-" * 30)
    logger.debug("User Question: %s", question)
    logger.debug("RAG Context: %s", context)
    system_prompt = get_tone_prompt(tone)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]

    try:
        res = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        answer = res.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ... (existing code for @app.get("/") home route)
