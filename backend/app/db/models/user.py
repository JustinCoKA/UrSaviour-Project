from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_user_id():
    return "U" + uuid.uuid4().hex[:4].upper()  # e.g. U7A2C

class User(Base):
    __tablename__ = "userAccounts"  # As per documentation

    user_id = Column("user_id", String(10), primary_key=True, default=generate_user_id)
    email = Column("email", String(255), unique=True, nullable=False)
    first_name = Column("first_name", String(50), nullable=False)
    last_name = Column("last_name", String(50), nullable=False)
    password = Column("password", String(255), nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)