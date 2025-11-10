#!/usr/bin/env python3
"""
Create auth tables (userAccounts, loginLogs) on the configured database.
Use this when you want to provision AWS RDS directly without running Docker.

Usage (from repo root):
  python3 scripts/create_rds_auth_tables.py

It reads DB settings from .env via app.core.config.Settings.
Set AUTH_DATABASE_URL (recommended) or DB_* fields to point to your RDS instance.
"""
from __future__ import annotations
import sys
from pathlib import Path

# Ensure we can import the backend package (app.*)
ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine
from app.db.models.base import Base
# Import models so they are registered with Base.metadata
from app.db.models.user import User  # noqa: F401
from app.db.models.login_log import LoginLog  # noqa: F401


def main() -> int:
    print("Using AUTH DB URL:")
    print(settings.auth_database_url())

    try:
        # Connectivity check
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected to database successfully.")
    except Exception as e:
        print("[ERROR] Could not connect to database:", e)
        return 1

    try:
        print("Creating tables if missing (userAccounts, loginLogs)...")
        Base.metadata.create_all(bind=engine)
        print("Done.")
    except Exception as e:
        print("[ERROR] Table creation failed:", e)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
