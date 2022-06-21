from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from articles_api.api.dependencies import get_current_active_user, get_db_user, get_db
from articles_api.core import schemas
from articles_api.core.enums import Roles
from articles_api.core.mapping import db_user_to_user
from articles_api.db import crud
from articles_api.core.schemas import User
from articles_api.db import models

from typing import List

router = APIRouter()


@router.get("/users/me/", response_model=User)
def read_users_me(current_user: models.User = Depends(get_current_active_user)
                       ) -> schemas.User:
    return db_user_to_user(current_user)

@router.get("/users/active_users_ids")
def get_active_users_ids(current_user: models.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)) -> List[int]:
    
    return [user_id for (user_id,) in crud.get_active_users_ids(db)]

@router.get("/users/users_ids_with_roles")
def get_users_ids_with_roles(roles: List[Roles] = Query(default=[]),
                             current_user: models.User = Depends(get_current_active_user),
                             db: Session = Depends(get_db)) -> List[int]:
    return [user_id for (user_id,) in set(crud.get_users_ids_with_roles(db, set(roles)))]


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(current_user: models.User = Depends(get_current_active_user),
             db_user: models.User = Depends(get_db_user)) -> schemas.User:
    return db_user_to_user(db_user)