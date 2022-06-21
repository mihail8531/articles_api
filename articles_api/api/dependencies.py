import traceback
from typing import Generator, List, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from articles_api.core.enums import ArticleStates, Roles
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

def get_users_by_ids(ids: List[int],
                     db: Session = Depends(get_db)) -> List[models.User]:
    users = crud.get_users_by_ids(db, ids)
    if len(users) < len(ids):
        raise HTTPException(status_code=409, detail="Ids list contains invalid user id")
    return users


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

def get_article(article_id: int,
                   db: Session = Depends(get_db)) -> models.Article:
    db_article = crud.get_article_by_id(db, article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail=f"Article with id {article_id} not found")
    return db_article

def get_draft_article(article: models.Article = Depends(get_article)) -> models.Article:
    if article.state != ArticleStates.draft:
        raise HTTPException(status_code=409, detail="Article must be a draft for publishing")
    return article

def get_db_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

get_writer_or_admin = RolesChecker(Roles.writer, Roles.admin)
get_reader_or_admin = RolesChecker(Roles.reader, Roles.admin)
get_writer_moderator_or_admin = RolesChecker(Roles.writer, Roles.moderator, Roles.admin)
get_admin = RolesChecker(Roles.admin)