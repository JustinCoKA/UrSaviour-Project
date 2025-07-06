# backend/init_db.py

from app.db.models.base import Base
from app.db.session import engine

# Create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
