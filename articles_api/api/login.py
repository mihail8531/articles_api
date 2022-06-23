from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from pytest import Session
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm as OA2PRF
from articles_api.core.auth import authenticate_user, register_user
from articles_api.core.enums import Roles
from articles_api.core.mapping import db_user_to_user
from articles_api.core.schemas import Token, User, UserCreate
from articles_api.core.security import (create_access_token,
                                        ACCESS_TOKEN_EXPIRE_MINUTES)
from .dependencies import get_db

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OA2PRF = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
def register(form_data: UserCreate, db: Session = Depends(get_db)):
    if form_data.username == "admin":
        user = register_user(db, form_data, Roles.admin)
    else:
        user = register_user(db, form_data, Roles.reader)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with given username already exists"
        )
    return db_user_to_user(user)
    
