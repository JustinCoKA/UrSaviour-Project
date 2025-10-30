# backend/app/db/models/login_log.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
from app.db.models.base import Base

class LoginLog(Base):
    __tablename__ = "loginLogs"

    log_id = Column(String(36), primary_key=True)
    user_id = Column(String(10), ForeignKey("userAccounts.user_id"))
    login_time = Column(DateTime, default=datetime.utcnow)