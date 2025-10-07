from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
	"""Dependency generator that yields a SQLAlchemy Session and ensures it's closed."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()