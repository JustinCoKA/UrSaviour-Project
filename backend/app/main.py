# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

cors_origins = settings.BACKEND_CORS_ORIGINS or ["*"]
dev_local_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
if len(cors_origins) == 1 and cors_origins[0] == "*":
    allow_origins = dev_local_origins
    allow_credentials = False
else:
    allow_origins = cors_origins
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

@app.get("/api/v1/health", include_in_schema=False)
def v1_health():
    return {"status": "ok"}

@app.get("/ready", include_in_schema=False)
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        return {"ready": False, "error": str(e)}

app.include_router(api_router, prefix=settings.API_PREFIX)
