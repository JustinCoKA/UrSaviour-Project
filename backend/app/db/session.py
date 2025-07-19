from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use environment variable for DB connection (Docker compatible)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://ursaviouruser:securepassword@db:3306/ursaviour")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
