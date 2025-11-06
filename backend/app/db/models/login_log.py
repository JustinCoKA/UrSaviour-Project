# backend/app/db/models/login_log.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from uuid import uuid4
from app.db.models.base import Base

class LoginLog(Base):
    __tablename__ = "loginLogs"

    # Column names following spec (camelCase in DB)
    log_id = Column("loginId", String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column("userId", String(5), ForeignKey("userAccounts.userId"), nullable=True)
    email = Column("email", String(255))
    attempted_at = Column("attemptedAt", DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column("ipAddress", String(45))
    is_successful = Column("isSuccessful", Boolean, default=False, nullable=False)
    failure_reason = Column("failureReason", String(255))