from articles_api.db import models
from articles_api.core import schemas


def db_user_to_user(db_user: models.User) -> schemas.User:
    roles = [x.role.value for x in db_user.roles]
    created_articles_ids = [x.id for x in db_user.created_articles]
    editor_for_articles_ids = [x.id for x in db_user.editor_for_articles]
    author_for_aritcles_ids = [x.id for x in db_user.author_for_articles]
    user = schemas.User(id=db_user.id,
                        is_active=db_user.is_active,
                        roles=roles,
                        email=db_user.email,
                        username=db_user.username,
                        created_articles_ids=created_articles_ids,
                        editor_for_articles_ids=editor_for_articles_ids,
                        author_for_aritcles_ids=author_for_aritcles_ids
                        )
    return user
    