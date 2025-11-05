from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserLogin, LoginResponse
from app.db.session import get_db
from app.services.auth import create_user, authenticate_user, create_access_token
from app.db.models.user import User
from app.core.config import settings
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Use the service function to create the user
    new_user = create_user(db, user)
    return new_user

@router.post("/login", response_model=LoginResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    # Authenticate user
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
