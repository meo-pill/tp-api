from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app import crud, schemas
from app.auth import (
    create_access_token,
    verify_password,
    get_current_active_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# ================== LOGIN ==================

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_username(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ================== ME ==================

@router.get("/me", response_model=schemas.UserResponse)
def read_me(
    current_user = Depends(get_current_active_user)
):
    return current_user

