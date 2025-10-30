from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate
import hashlib
import bcrypt

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