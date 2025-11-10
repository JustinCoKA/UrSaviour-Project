# backend/app/db/models/user.py

from sqlalchemy import Column, String, DateTime, event, select, func
from datetime import datetime
from app.db.models.base import Base
from sqlalchemy.orm import Session

class User(Base):
    __tablename__ = "userAccounts"

    # Use camelCase column names to match the spec while keeping Python attributes snake_case
    user_id = Column("userId", String(5), primary_key=True)
    email = Column("email", String(255), unique=True, nullable=False)
    first_name = Column("firstName", String(50), nullable=False)
    last_name = Column("lastName", String(50), nullable=False)
    password = Column("passwordHash", String(255), nullable=False)
    created_at = Column("createdAt", DateTime, default=datetime.utcnow)

# --- Event hook: Create user_id from "U0001" --- #
@event.listens_for(User, "before_insert")
def generate_user_id(mapper, connection, target):
    result = connection.execute(
        select(func.max(User.user_id)).select_from(User)
    ).scalar()

    next_id = 1

    if result and result.startswith("U") and result[1:].isdigit():
        next_id = int(result[1:]) + 1

    target.user_id = f"U{next_id:04d}"