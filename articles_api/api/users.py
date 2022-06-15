from fastapi import APIRouter, Depends
from articles_api.api.dependencies import get_current_active_user
from articles_api.core.mapping import db_user_to_user

from articles_api.core.schemas import User
from articles_api.db import models


router = APIRouter()


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return db_user_to_user(current_user)
