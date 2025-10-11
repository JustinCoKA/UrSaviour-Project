# backend/app/core/config.py
from typing import Optional, List, Union
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

class Settings(BaseSettings):
    # Config for pydantic-settings v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Base ---
    APP_ENV: str = Field(default="dev", description="dev|staging|prod")
    PROJECT_NAME: str = "UrSaviour"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # --- CORS ---
    # allow str OR list, normalize to list in validator
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = Field(default="*")
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        # None/empty -> wildcard for dev
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        s = str(v).strip()
        if not s:
            return ["*"]
        # Try JSON list first
        if s.startswith("["):
            try:
                arr = json.loads(s)
                return [str(x).strip() for x in arr if str(x).strip()]
            except Exception:
                pass
        # Fallback: comma-separated
        return [o.strip() for o in s.split(",") if o.strip()]

    # --- Database ---
    DB_SCHEME: str = "mysql+pymysql"
    DB_HOST: str = Field(default="db", description="Database host (use RDS endpoint in production)")
    DB_PORT: int = 3306
    DB_USER: str = Field(default="ursaviour", description="Database username")
    DB_PASSWORD: SecretStr = Field(default=SecretStr("secret"), description="Database password")
    DB_NAME: str = Field(default="ursaviour", description="Database name")
    DATABASE_URL: Optional[str] = Field(default=None, description="Complete database URL (overrides other DB settings)")
    
    # AWS RDS specific settings
    DB_SSL_MODE: str = Field(default="PREFERRED", description="SSL mode for database connection")
    DB_CHARSET: str = Field(default="utf8mb4", description="Database charset")

    def database_url(self) -> str:
        # Return explicit DATABASE_URL or build from fields
        if self.DATABASE_URL:
            return self.DATABASE_URL
        pwd = self.DB_PASSWORD.get_secret_value()
        ssl_params = f"&ssl_mode={self.DB_SSL_MODE}" if self.APP_ENV == "prod" else ""
        return f"{self.DB_SCHEME}://{self.DB_USER}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset={self.DB_CHARSET}{ssl_params}"

    # --- JWT ---
    SECRET_KEY: SecretStr = SecretStr("change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Storage / ETL ---
    STORAGE_BACKEND: str = Field(default="local", description="local|s3")
    WATCH_FOLDER: str = "/data/watch"  # used only in dev
    AWS_REGION: str = "ap-southeast-2"
    S3_BUCKET_NAME: str = "ursaviour-pamphlets"
    S3_PREFIX: str = "prod"

    # --- AWS (optional, use IAM role in prod if possible) ---
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = None
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = None

    # --- Email ---
    SMTP_HOST: str = "mailhog"  # dev default
    SMTP_PORT: int = 1025
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    MAIL_FROM: str = "noreply@ursaviour.local"

settings = Settings()
