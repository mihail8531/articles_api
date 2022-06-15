from sqlalchemy.orm import Session
from .models import Article, User, Role
from articles_api.core.schemas import ArticleCreate, UserCreate
from articles_api.core.enums import ArticleStates, Roles
from articles_api.core.security import get_password_hash


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

def create_article(db: Session,
                   article: ArticleCreate,
                   user: User) -> Article:
    db_article = Article(**article.dict(),
                         state=ArticleStates.draft,
                         creator_id=user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

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