import email
from sqlalchemy.orm import Session

from articles_api.db import models
from articles_api.core import schemas



def db_user_to_user(db_user: models.User) -> schemas.User:
    user = schemas.User(id=db_user.id,
                        is_active=db_user.is_active,
                        roles=[x.role.value for x in db_user.roles],
                        email=db_user.email,
                        username=db_user.username,
                        created_articles_ids=[x.id for x in db_user.created_articles],
                        editor_for_articles_ids=[x.id for x in db_user.editor_for_articles],
                        author_for_aritcles_ids=[x.id for x in db_user.author_for_articles]
                        )
    return user