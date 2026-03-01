from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshRequest,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# 🔹 Register
@router.post("/register", response_model=TokenResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=hash_password(user.password),
        role="owner",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token_value = create_refresh_token()

    refresh_token = RefreshToken(
        token=refresh_token_value,
        user_id=new_user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        is_revoked=False,
    )

    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
    }


# 🔹 Login
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token_value = create_refresh_token()

    refresh_token = RefreshToken(
        token=refresh_token_value,
        user_id=db_user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        is_revoked=False,
    )

    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
    }


# 🔹 Refresh (Rotation)
@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):

    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == request.refresh_token)
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if db_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked",
        )

    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Revoke old token
    db_token.is_revoked = True

    # Create new refresh token
    new_refresh_token_value = create_refresh_token()

    new_refresh_token = RefreshToken(
        token=new_refresh_token_value,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        is_revoked=False,
    )

    db.add(new_refresh_token)
    db.commit()

    new_access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token_value,
        "token_type": "bearer",
    }


# 🔹 Logout
@router.post("/logout")
def logout(request: RefreshRequest, db: Session = Depends(get_db)):

    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == request.refresh_token)
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    db_token.is_revoked = True
    db.commit()

    return {"message": "Logged out successfully"}