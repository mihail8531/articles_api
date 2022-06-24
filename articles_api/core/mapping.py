from articles_api.core.enums import CommentaryStates
from articles_api.db import models
from articles_api.core import schemas


def db_user_to_user(db_user: models.User) -> schemas.User:
    roles = [x.role for x in db_user.roles]
    created_articles_ids = [x.id for x in db_user.created_articles]
    editor_for_articles_ids = [x.id for x in db_user.editor_for_articles]
    author_for_aritcles_ids = [x.id for x in db_user.author_for_articles]
    commentaries_ids = [x.id for x in db_user.commentaries]
    user = schemas.User(id=db_user.id,
                        is_active=db_user.is_active,
                        roles=roles,
                        email=db_user.email,
                        username=db_user.username,
                        created_articles_ids=created_articles_ids,
                        editor_for_articles_ids=editor_for_articles_ids,
                        author_for_aritcles_ids=author_for_aritcles_ids,
                        commentaries_ids=commentaries_ids
                        )
    return user

def db_article_to_article(db_article: models.Article) -> schemas.Article:
    authors_ids = [author.id for author in db_article.authors]
    editors_ids = [editor.id for editor in db_article.editors]
    commentaries_ids = [x.id for x in db_article.commentaries if x.state == CommentaryStates.approved]
    article = schemas.Article(id=db_article.id,
                              name=db_article.name,
                              content=db_article.content,
                              creator_id=db_article.creator_id,
                              state=db_article.state,
                              editors_ids=editors_ids,
                              authors_ids=authors_ids,
                              commentaries_ids=commentaries_ids, 
                              )
    return article