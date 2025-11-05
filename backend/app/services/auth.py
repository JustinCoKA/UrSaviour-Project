from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate
import hashlib
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.core.config import settings

# Use bcrypt directly to avoid passlib initialization issues

# Hash a password with SHA-256 pre-hashing and direct bcrypt usage
def hash_password(password: str) -> str:
    # Pre-hash with SHA-256 to ensure consistent length and avoid bcrypt 72-byte limit
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Use bcrypt directly with the SHA-256 hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sha256_hash.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Verify a password with SHA-256 pre-hashing and direct bcrypt usage
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Pre-hash with SHA-256 to match the hashing process
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    # Use bcrypt directly to verify
    return bcrypt.checkpw(sha256_hash.encode('utf-8'), hashed_password.encode('utf-8'))

# Create a new user
def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_pw = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authenticate user by email and password
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

# Create JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Verify JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None