# backend/app/db/models/login_log.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from datetime import datetime
from app.db.models.base import Base

def generate_login_log_id(context):
    """Generate log ID in format L0001, L0002, etc."""
    from sqlalchemy import select, func
    connection = context.connection
    
    # Get the maximum numeric part of existing IDs
    result = connection.execute(
        select(func.max(func.cast(func.substr(LoginLog.__table__.c.loginId, 2), Integer)))
    ).scalar()
    
    next_id = (result or 0) + 1
    return f"L{next_id:04d}"

class LoginLog(Base):
    __tablename__ = "loginLogs"

    # Column names following spec (camelCase in DB)
    log_id = Column("loginId", String(10), primary_key=True, default=generate_login_log_id)
    user_id = Column("userId", String(5), ForeignKey("userAccounts.userId"), nullable=True)
    email = Column("email", String(255))
    attempted_at = Column("attemptedAt", DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column("ipAddress", String(45))
    is_successful = Column("isSuccessful", Boolean, default=False, nullable=False)
    failure_reason = Column("failureReason", String(255))