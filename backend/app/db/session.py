# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Build DB connection URL
DATABASE_URL = settings.database_url()
# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# Create session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Common dependency for routers
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()