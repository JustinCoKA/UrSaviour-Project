# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
# from app.api import auth, products, watchlist, admin, etl  # to be added later

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (to be added in Phase 3~)
# app.include_router(auth.router, prefix=settings.API_PREFIX)
# ...

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
