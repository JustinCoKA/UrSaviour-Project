# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.session import engine  # DB engine for readiness probe
from app.core.config import settings  # settings (CORS origins, metadata)
from app.api.v1.router import api_router

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Enable CORS (dev: wide open, prod: restrict to your domains)
# Configure CORS carefully: browsers forbid allow-credentials with allow-origin='*'
cors_origins = settings.BACKEND_CORS_ORIGINS or ["*"]

# Developer-friendly default origins when wildcard is configured (do not use in prod)
dev_local_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

if len(cors_origins) == 1 and cors_origins[0] == "*":
    # Expand wildcard in dev to include common local frontend origins. Browsers will
    # only accept credentials if the Access-Control-Allow-Origin header matches the
    # request origin exactly, so do NOT set allow_credentials when using '*'.
    allow_origins = dev_local_origins
    allow_credentials = False
else:
    allow_origins = cors_origins
    # When origins are explicitly provided, allow credentials by default
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Liveness probe: process is up
@app.get("/health")
def health():
    # Keep this lightweight; no external checks
    return {"status": "ok"}

# Readiness probe: checks DB connectivity
@app.get("/ready")
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        # Do NOT crash the app; expose error for quick diagnosis
        return {"ready": False, "error": str(e)}

# Routers will be added from Phase 3 onwards:
# from app.api import auth, products, watchlist, admin, etl
# app.include_router(auth.router, prefix=settings.API_PREFIX)
# app.include_router(products.router, prefix=settings.API_PREFIX)
# app.include_router(watchlist.router, prefix=settings.API_PREFIX)
# app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin")
# app.include_router(etl.router, prefix=settings.API_PREFIX)

# Include the v1 API router
app.include_router(api_router, prefix=settings.API_PREFIX)
