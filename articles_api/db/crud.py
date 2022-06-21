from typing import Iterator, List, Set, Tuple
from sqlalchemy.orm import Session

from articles_api.core import schemas
from .models import Article, AuthorArticle, EditorArticle, User, Role
from articles_api.core.schemas import ArticleCreate, UserCreate
from articles_api.core.enums import ArticleStates, Roles
from articles_api.core.security import get_password_hash

from articles_api.db import models


def create_user(db: Session, user: UserCreate, role: Roles) -> User:
    db_user = User(username=user.username,
                   email=user.email,
                   hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_role = Role(owner_id=db_user.id,
                   role=role)
    db.add(db_role)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, id: int) -> User:
    return db.query(User).filter(User.id == id).first()

def get_users_by_ids(db: Session, ids: List[int]) -> List[User]:
    return db.query(User).filter(User.id in ids).all()

def get_active_users_ids(db: Session) -> Iterator[Tuple[int]]:
    return db.query(User).values(User.id)

def get_users_ids_with_roles(db: Session, roles: Set[Roles]) -> Iterator[Tuple[int]]:
    return db.query(Role).filter(Role.role.in_(roles)).values(Role.owner_id)

def set_user_active(db: Session, db_user: models.User, is_active: bool) -> models.User:
    db.query(models.User).filter(models.User.id == db_user.id).update({models.User.is_active: is_active})
    db.commit()
    db.refresh(db_user)
    return db_user

def add_authors_by_ids(db: Session, db_article: Article,
                       ids: List[int]) -> Article:
    article_authors = [AuthorArticle(author_id=author_id,
                                     article_id=db_article.id) for author_id in ids]
    db.add_all(article_authors)
    db.commit()
    db.refresh(db_article)
    return db_article

def remove_authors_by_ids(db: Session, db_article: Article,
                          ids: List[int]) -> Article:
    db.query(AuthorArticle).filter((AuthorArticle.article_id == db_article.id) &
                                   (AuthorArticle.author_id in ids)).delete()
    db.commit()
    db.refresh(db_article)
    return db_article

def add_editors_by_ids(db: Session, db_article: Article,
                       ids: List[int]) -> Article:
    article_editors = [EditorArticle(editor_id=editor_id,
                                     article_id=db_article.id) for editor_id in ids]
    db.add_all(article_editors)
    db.commit()
    db.refresh(db_article)
    return db_article

def remove_editors_by_ids(db: Session, db_article: Article,
                          ids: List[int]) -> Article:
    db.query(EditorArticle).filter((EditorArticle.article_id == db_article.id) &
                                   (EditorArticle.editor_id in ids)).delete()
    db.commit()
    db.refresh(db_article)
    return db_article

def create_article(db: Session,
                   article: ArticleCreate,
                   user: User) -> Article:
    db_article = Article(**article.dict(),
                         state=ArticleStates.draft,
                         creator_id=user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    db_article_author = AuthorArticle(author_id=user.id,
                                      article_id=db_article.id)
    db.add(db_article_author)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_article_by_id(db: Session,
                      article_id: int) -> Article:
    return db.query(Article).filter(Article.id == article_id).first()

def get_articles_by_state(db: Session,
                          state: ArticleStates) -> List[Article]:
    return db.query(Article).filter(Article.state == state).all()

def get_articles_by_author(db: Session,
                           user: User) -> List[Article]:
    return db.query(Article).filter(Article.creator_id == user.id).all()

def edit_article(db: Session,
                 db_article: Article,
                 article: schemas.ArticleCreate) -> Article:
    db.query(Article).filter(Article.id == db_article.id).update(article.dict())
    db.commit()
    db.refresh(db_article)
    return db_article

def set_article_state(db: Session,
                      db_aritcle: Article,
                      article_state: ArticleStates) -> Article:
    db.query(Article).filter(Article.id == db_aritcle.id).update({Article.state: article_state})
    db.commit()
    db.refresh(db_aritcle)
    return db_aritcle



def add_role(db: Session,
             user: User,
             role: Roles) -> User:
    db_role = Role(role=role,
                   owner_id=user.id)
    db.add(db_role)
    db.commit()
    db.refresh(user)
    return user

def remove_role(db: Session,
                user: User,
                role: Roles) -> User:
    db.query(Role).filter((Role.owner_id == user.id) & (Role.role == role)).delete()
    db.commit()
    db.refresh(user)
    return user