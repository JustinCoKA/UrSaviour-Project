from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserLogin, LoginResponse
from app.db.session import get_db
from app.services.auth import create_user, authenticate_user, create_access_token, verify_password
from app.db.models.user import User
from app.db.models.login_log import LoginLog
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
def login_user(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    # Detect client IP (supports proxies)
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else None)

    # Determine user and outcome
    db_user = db.query(User).filter(User.email == login_data.email).first()
    is_success = False
    failure_reason = None

    if db_user and verify_password(login_data.password, db_user.password):
        is_success = True
        user = db_user
    else:
        user = None
        failure_reason = "User Not Found" if db_user is None else "Incorrect Password"

    # Log the attempt
    try:
        db.add(LoginLog(
            user_id=(db_user.user_id if db_user else None),
            email=login_data.email,
            ip_address=ip,
            is_successful=is_success,
            failure_reason=failure_reason,
        ))
        db.commit()
    except Exception:
        db.rollback()

    if not is_success:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Generate token on success
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}
