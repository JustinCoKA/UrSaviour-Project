from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

# Declare the base class for all ORM models
Base = declarative_base()

# Abstract base model with common fields
class BaseModel(Base):
    __abstract__ = True  # This class won't be mapped to a table

    id = Column(Integer, primary_key=True, index=True)  # Primary key
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp for creation
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp for update
