from typing import Literal, Union
from sqlalchemy.orm import Session
from articles_api.core.enums import Roles
from articles_api.core.schemas import UserCreate
from articles_api.core.security import verify_password
from articles_api.db.crud import create_user, get_user_by_username
from articles_api.db.models import User


def authenticate_user(db: Session,
                      username: str,
                      password: str
                      ) -> Union[User, Literal[False]]:
    db_user = get_user_by_username(db, username)
    if not db_user:
        return False
    if not verify_password(password, db_user.hashed_password):
        return False
    return db_user


def register_user(db: Session,
                  form_data: UserCreate,
                  role: Roles
                  ) -> Union[User, Literal[False]]:
    db_user = get_user_by_username(db, form_data.username)
    if db_user:
        return False
    return create_user(db, form_data, role)

