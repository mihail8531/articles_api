import traceback
from typing import Generator, List, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from articles_api.core.enums import Roles
from articles_api.core.schemas import TokenData
from articles_api.db.database import SessionLocal
from articles_api.config import config
from articles_api.core import security
from articles_api.db import crud, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenData(id=payload.get("sub"))
    except (jwt.JWTError, ValidationError):
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.get_user_by_id(db, id=int(token_data.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RolesChecker:
    def __init__(self, *roles: Roles) -> None:
        self.roles = set(roles)
    
    @staticmethod
    def have_user_one_of_roles(user: models.User, roles: Set[Roles]) -> bool:
        user_roles = {role.role for role in user.roles}
        if roles.intersection(user_roles):
            return True
        return False
    
    def __call__(self,
                 user: models.User = Depends(get_current_active_user)
    ) -> models.User:
        if not self.have_user_one_of_roles(user, self.roles):
            raise HTTPException(status_code=403, detail="Access denied")
        return user

get_writer_or_admin = RolesChecker(Roles.writer, Roles.admin)
get_reader_or_admin = RolesChecker(Roles.reader, Roles.admin)
get_admin = RolesChecker(Roles.admin)