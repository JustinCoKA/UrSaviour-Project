from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Build separate engines for auth (default) and products (optional remote)
AUTH_DATABASE_URL = settings.auth_database_url()
PRODUCTS_DATABASE_URL = settings.products_database_url()

# Default engine/session used across most of the app (auth, users, etc.)
engine = create_engine(AUTH_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Products-specific engine/session (may point to EC2/leader DB)
products_engine = create_engine(PRODUCTS_DATABASE_URL, pool_pre_ping=True)
ProductsSessionLocal = sessionmaker(bind=products_engine, autoflush=False, autocommit=False)


def get_db():
	"""Dependency generator for the default (auth) database session."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_products_db():
	"""Dependency generator for the products database session."""
	db = ProductsSessionLocal()
	try:
		yield db
	finally:
		db.close()