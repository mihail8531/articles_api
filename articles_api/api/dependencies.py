import traceback
from typing import Generator, List, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from articles_api.core.enums import ArticleStates, CommentaryStates, Roles
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


def get_article(article_id: int,
                   db: Session = Depends(get_db)) -> models.Article:
    db_article = crud.get_article_by_id(db, article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail=f"Article with id {article_id} not found")
    return db_article


def get_db_user(user_id: int, db: Session = Depends(get_db)) -> models.User:
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_db_commentary(commentary_id: int, db: Session = Depends(get_db)):
    db_commentary = crud.get_commentary_by_id(db, commentary_id)
    if not db_commentary:
        raise HTTPException(status_code=404, detail="Commentary not found")
    return db_commentary


class RolesChecker:
    def __init__(self, *roles: Roles) -> None:
        self.roles = set(roles)
    
    def __call__(self,
                 user: models.User = Depends(get_current_active_user)
    ) -> models.User:
        if not user.have_one_of_roles(self.roles):
            raise HTTPException(status_code=403, detail="Access denied")
        return user


get_writer_or_admin = RolesChecker(Roles.writer, Roles.admin)
get_reader_or_admin = RolesChecker(Roles.reader, Roles.admin)
get_writer_moderator_or_admin = RolesChecker(Roles.writer, Roles.moderator, Roles.admin)
get_admin = RolesChecker(Roles.admin)
get_moderator_or_admin = RolesChecker(Roles.moderator, Roles.admin)


class ArticleStateChecker:
    def __init__(self, state: ArticleStates) -> None:
        self.state = state

    def __call__(self, article: models.Article=Depends(get_article)) -> models.Article:
        if article.state != self.state:
            raise HTTPException(status_code=409, detail=f"Article's state must be a {self.state}")
        return article


get_draft_article = ArticleStateChecker(ArticleStates.draft)
get_approved_article = ArticleStateChecker(ArticleStates.approved)
get_rejected_article = ArticleStateChecker(ArticleStates.rejected)
get_published_article = ArticleStateChecker(ArticleStates.published) 


class CommentaryStateChecker:
    def __init__(self, state: CommentaryStates) -> None:
        self.state = state
    
    def __call__(self, commentary: models.Commentary=Depends(get_db_commentary)) -> models.Commentary:
        if commentary.state != self.state:
            raise HTTPException(status_code=409, detail=f"Commentary's state must be a {self.state}")
        return commentary

get_published_commentary = CommentaryStateChecker(CommentaryStates.published)
get_published_approved = CommentaryStateChecker(CommentaryStates.approved)
get_published_rejected = CommentaryStateChecker(CommentaryStates.rejected)
