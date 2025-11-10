# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.session import engine
from app.db.models.base import Base
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

cors_origins = settings.BACKEND_CORS_ORIGINS or ["*"]
dev_local_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5500",
    "https://www.ursaviour.com",
    "https://ursaviour.com",
    "http://www.ursaviour.com",
    "http://ursaviour.com"
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

@app.on_event("startup")
def ensure_auth_tables():
    """Create auth tables (userAccounts, loginLogs) if they don't exist.
    Safe to call repeatedly; only affects the default auth engine.
    """
    try:
        Base.metadata.create_all(bind=engine)
        # Light-touch, idempotent adjustments for dev environment
        with engine.begin() as conn:
            # Make userId nullable and ensure email column exists on loginLogs
            try:
                conn.execute(text("ALTER TABLE loginLogs MODIFY COLUMN userId varchar(5) NULL"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE loginLogs ADD COLUMN IF NOT EXISTS email varchar(255)"))
            except Exception:
                pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Table auto-create skipped: {e}")

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

@app.get("/api/health", include_in_schema=False)
def api_health():
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
# Import watchlist routes that live at project root-level under backend/
# In the container, ./backend is mounted to /app, so the module path is just 'watchlist_routes'
try:
  try:
    from watchlist_routes import router as watchlist_router
    app.include_router(watchlist_router)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"Optional watchlist routes not loaded: {e}")

from fastapi import FastAPI
from app.api.v1 import watchlist  # 👈 FIXED IMPORT

app = FastAPI()

# include main API router
app.include_router(api_router, prefix=settings.API_PREFIX)

# include watchlist router
app.include_router(watchlist.router)

