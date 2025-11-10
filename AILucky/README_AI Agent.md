# AILucky – AI Assistant (FastAPI + RAG)

This folder contains a small FastAPI app that exposes a chat endpoint and a minimal UI for an AI assistant. On startup it can optionally ingest CSV/PDF files from S3 into a local Chroma vector database and use them as context for answers (RAG).

## Quick start

Prereqs
- Python 3.11+
- macOS or Linux (Windows WSL is fine)
- Optional: AWS credentials and an S3 bucket if you want data ingestion

Setup
1) Create and activate a virtual environment

```zsh
cd "$(git rev-parse --show-toplevel)/AILucky"
python3 -m venv Luckyenv
source Luckyenv/bin/activate
```

2) Install dependencies
```zsh
pip install -r requirements.txt
```

3) Add environment variables (create `.env` in `AILucky/`)
```dotenv
# Required for OpenAI - Create and use your own Open API Key 
OPENAI_API_KEY=sk-...

# Optional: control console log level: DEBUG|INFO|WARNING|ERROR
LOG_LEVEL=WARNING

#enable S3 ingestion at startup - Using the .env.example for information bellow 
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=ap-southeast-2
BUCKET_NAME=your-s3-bucket
```

4) Run the app
```zsh
uvicorn app:app --reload
```

5) Open the chat UI
- Visit http://127.0.0.1:8000/ to load the chat page from the app itself, or
- Open `frontend/src/Chat-page.html` with VS Code “Live Server”. The script calls `http://127.0.0.1:8000/chat` by default in local mode.

## What it does
- Startup
  - If `BUCKET_NAME` is set, the app lists objects in the bucket, reads `.csv` and `.pdf`, extracts text safely, embeds up to the first ~2000 characters, and stores embeddings in a local Chroma DB folder `chroma_db/`.
  - Resilient to empty or undecodable files; such files are skipped with a warning.
- Chat
  - POST `/chat` with your question; the app embeds the question, retrieves top documents from Chroma, and asks the model (`gpt-4o-mini`) to answer using that context.

## Endpoints

- GET `/` – renders `Chat-page.html` (simple chat UI)
- POST `/chat`
  - Request
    - JSON: `{ "message": "How much is Mineral Water?", "tone": "default" }`
    - `tone` is optional: `default|friendly|technical|teacher`
  - Response
    - JSON: `{ "answer": "..." }`
- GET `/api/v1/products/`
  - Returns a small sample payload shaped like the product API used by the site frontend (for local UI dev).

Examples
```zsh
# Ask a question from terminal
curl -s http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "How much is Mineral Water?", "tone": "friendly"}' | jq
```

## Data ingestion (optional)
If you set `BUCKET_NAME`, the app will try to load `.csv` and `.pdf` files from S3 at startup.

Notes
- CSV
  - Decoding tries UTF‑8 then latin‑1; if parsing fails, raw text is used as a fallback.
- PDF
  - Uses `PyPDF2` and skips pages that fail to extract text.
- Skips non-supported types and empty/undecodable bodies.
- Embedding model: `text-embedding-3-small`.

To re-load data without restarting, stop and start uvicorn (simple dev flow). If you prefer, we can add a `/admin/reindex` endpoint later.

## Logging
- Controlled via `LOG_LEVEL` env (`DEBUG|INFO|WARNING|ERROR`). Default: `WARNING` to keep the console tidy.
- Messages are emitted under logger name `AILucky`.
- To reduce uvicorn noise further, you can run:

```zsh
uvicorn app:app --reload --log-level warning
```

## Troubleshooting

- Server prints: `Directory 'static' does not exist`
  - The app now resolves and auto-creates a local `frontend/src` folder inside `AILucky` if missing to prevent this error.

- `⚠️ BUCKET_NAME not set; skipping S3 data load`
  - Informational: the app will run fine without S3 ingestion.

- `expected string or bytes-like object, got 'NoneType'`
  - Fixed in readers: we now guard against `None` bodies and empty objects from S3.

- Frontend requests `GET /api/v1/products/` 404
  - The full product API lives in `backend/` (Docker or local DB). For local UI dev, this AILucky app returns a small sample at `/api/v1/products/`.

- Chat page loads but no messages appear
  - Make sure the server is running on `http://127.0.0.1:8000`.
  - Open the browser console; network errors will be shown if `/chat` is unreachable.

## Project layout (this folder)

- `app.py` – FastAPI app, S3 ingestion, Chroma RAG, `/chat` endpoint, and a basic home page.
- `requirements.txt` – Python dependencies.
- `chroma_db/` – Local persistent Chroma store (created at runtime).
- `frontend/src/` – The app can serve the chat page; the main site’s rich frontend also lives at repo root under `frontend/src/`.

## Safety and costs
- OpenAI usage incurs cost. Keep `LOG_LEVEL=INFO` or `WARNING` and avoid loops.
- Limit context size when adding to Chroma; we currently slice to ~2000 characters per file for embeddings to control token usage.

## Next steps (optional)
- Add `/search` endpoint that returns nearest documents and scores.
- Add `/admin/reindex` to reload S3 data on demand.
- Persist simple chat history in the UI; add typing indicator.
- Switch to environment-based model configuration.

---

If you want, I can wire up a `/search` endpoint and a reindex route next so you can refresh data without restarting the server.
