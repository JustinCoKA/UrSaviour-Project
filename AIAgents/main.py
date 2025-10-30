# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import rag_query
from aws_connector import download_from_s3
from embedding_loader import load_data_to_chroma

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5502/frontend/src/Chat-page.html"],  # use your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("🚀 Starting AI Agent Server...")
    download_from_s3()
    load_data_to_chroma()
    print("✅ Data loaded and embeddings ready.")

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    question = body.get("message", "")
    tone = body.get("tone", "default")
    print(f"🧠 Question: {question} | 🎭 Tone: {tone}")
    answer = rag_query(question, tone)
    return {"answer": answer}


