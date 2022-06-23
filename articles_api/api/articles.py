from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.api.dependencies import (RolesChecker, get_current_active_user,
                                           get_db, get_article, get_draft_article,
                                           get_writer_or_admin, get_reader_or_admin,
                                           get_writer_moderator_or_admin)
from articles_api.core.enums import ArticleStates, Roles
from articles_api.core.mapping import db_article_to_article
from articles_api.db import crud
from articles_api.core.schemas import Article, ArticleCreate, User
from articles_api.db import models


router = APIRouter()

@router.post("/articles/create", response_model=Article)
def create_article(article_create: ArticleCreate,
                   user: models.User = Depends(get_writer_or_admin),
                   db: Session = Depends(get_db)
) -> Article:
    db_aritcle = crud.create_article(db, article_create, user)
    return db_article_to_article(db_aritcle)

@router.get("/articles/my_created_articles")
def get_my_created_articles_ids(user: models.User = Depends(get_current_active_user),
                                db: Session = Depends(get_db)) -> List[int]:
    return [article.id for article in user.created_articles]

@router.get("/articles/my_edited_articles")
def get_my_edited_articles_ids(user: models.User = Depends(get_current_active_user),
                               db: Session = Depends(get_db)) -> List[int]:
    return [article.id for article in user.editor_for_articles]

@router.get("/articles/my_authored_articles")
def get_my_authored_articles_ids(user: models.User = Depends(get_current_active_user),
                                 db: Session = Depends(get_db)) -> List[int]:
    return [article.id for article in user.author_for_articles]

@router.get("/articles/approved_articles_ids")
def get_approved_articles_ids(user: models.User = Depends(get_reader_or_admin),
                              db: Session = Depends(get_db)) -> List[int]:
    return [article.id for article in crud.get_articles_by_state(db, ArticleStates.approved)]

@router.get("/articles/published_articles_ids")
def get_published_articles_ids(user: models.User = Depends(get_writer_moderator_or_admin),
                               db: Session = Depends(get_db)) -> List[int]:
    
    if not RolesChecker.have_user_one_of_roles(user, {Roles.moderator, Roles.admin}):
        return [article.id for article in crud.get_articles_by_author(db, user)
                if article.state == ArticleStates.published]
    return [article.id for article in crud.get_articles_by_state(db, ArticleStates.published)]

@router.patch("/articles/{article_id}/edit", response_model=Article) 
def edit_article(article: ArticleCreate,
                 db_article: models.Article = Depends(get_draft_article),
                 user: models.User = Depends(get_writer_or_admin),
                 db: Session = Depends(get_db)):
    is_creator = user.id == db_article.creator_id
    is_editor = user.id in {editor.id for editor in db_article.editors}
    is_author = user.id in {author.id for author in db_article.authors}
    if not (is_creator or is_editor or is_author):
        raise HTTPException(status_code=403, detail="Access denied")
    crud.edit_article(db, db_article, article)
    return db_article_to_article(db_article)

@router.patch("/articles/{article_id}/publish")
def publish_article(db_article: models.Article = Depends(get_draft_article),
                    user: models.User = Depends(get_writer_or_admin),
                    db: Session = Depends(get_db)) -> Article:
    if (user.id != db_article.creator_id):
        raise HTTPException(status_code=403, detail="Access denied")
    crud.set_article_state(db, db_article, ArticleStates.published) 
    return db_article_to_article(db_article)

@router.patch("/articles/{article_id}/unpublish")
def unpublish_article(db_article: models.Article = Depends(get_draft_article),
                    user: models.User = Depends(get_writer_or_admin),
                    db: Session = Depends(get_db)) -> Article:
    if (user.id != db_article.creator_id):
        raise HTTPException(status_code=403, detail="Access denied")
    crud.set_article_state(db, db_article, ArticleStates.draft) 
    return db_article_to_article(db_article)

# TODO remove copypast in methods: add_authors, remove_authors, add_editors, remove_editors 
@router.patch("/articles/{article_id}/add_authors") 
def add_authors(ids: List[int],
                db_article: models.Article = Depends(get_draft_article),
                user: models.User = Depends(get_writer_or_admin),
                db: Session = Depends(get_db)) -> Article:
    if (user.id != db_article.creator_id):
        raise HTTPException(status_code=403, detail="Access denied")
    if len(crud.get_users_by_ids(db, ids)) < len(ids):
        raise HTTPException(status_code=409, detail="Ids list contains invalid user id")
    authors_ids = {author.id for author in db_article.authors}
    if any(user_id in authors_ids for user_id in ids):
        raise HTTPException(status_code=409, detail="At list one of the given users already an author")
    crud.add_authors_by_ids(db, db_article, ids)
    return db_article_to_article(db_article)

@router.delete("/articles/{article_id}/remove_authors") 
def remove_authors(ids: List[int],
                   db_article: models.Article = Depends(get_draft_article),
                   user: models.User = Depends(get_writer_or_admin),
                   db: Session = Depends(get_db)) -> Article:
    if (user.id != db_article.creator_id):
        raise HTTPException(status_code=403, detail="Access denied")
    if len(crud.get_users_by_ids(db, ids)) < len(ids):
        raise HTTPException(status_code=409, detail="Ids list contains invalid user id")
    authors_ids = {author.id for author in db_article.authors}
    if any(user_id not in authors_ids for user_id in ids):
        raise HTTPException(status_code=409, detail="At list one of the given users is not an author")
    if (user.id in ids):
        raise HTTPException(status_code=409, detail="Can't remove creator from authors")
    crud.remove_authors_by_ids(db, db_article, ids)
    return db_article_to_article(db_article)
    
@router.patch("/articles/{article_id}/add_editors")
def add_editors(ids: List[int],
                db_article: models.Article = Depends(get_draft_article),
                user: models.User = Depends(get_writer_or_admin),
                db: Session = Depends(get_db)) -> Article:
    if (user.id != db_article.creator_id):
        raise HTTPException(status_code=403, detail="Access denied")
    if len(crud.get_users_by_ids(db, ids)) < len(ids):
        raise HTTPException(status_code=409, detail="Ids list contains invalid user id")
    editors_ids = {editor.id for editor in db_article.editors}
    if any(user_id in editors_ids for user_id in ids):
        raise HTTPException(status_code=409, detail="At list one of the given users already an editor")
    crud.add_editors_by_ids(db, db_article, ids)
    return db_article_to_article(db_article)

@router.delete("/articles/{article_id}/remove_editors") 
def remove_editors(ids: List[int],
                   db_article: models.Article = Depends(get_draft_article),
                   user: models.User = Depends(get_writer_or_admin),
                   db: Session = Depends(get_db)) -> Article:
    if (user.id != db_article.creator_id):
        raise HTTPException(status_code=403, detail="Access denied")
    if len(crud.get_users_by_ids(db, ids)) < len(ids):
        raise HTTPException(status_code=409, detail="Ids list contains invalid user id")
    editors_ids = {editor.id for editor in db_article.editors}
    if any(user_id not in editors_ids for user_id in ids):
        raise HTTPException(status_code=409, detail="At list one of the given users is not an editor")
    crud.remove_editors_by_ids(db, db_article, ids)
    return db_article_to_article(db_article)



@router.get("/articles/{article_id}", response_model=Article)
def get_aritcle(db_article = Depends(get_article),
                user: models.User = Depends(get_current_active_user)) -> Article:
    res_article = db_article_to_article(db_article)
    is_creator = user.id == db_article.creator_id
    is_admin = Roles.admin in user.roles
    if is_creator or is_admin:
        return res_article
    is_editor = user.id in {editor.id for editor in db_article.editors}
    is_author = user.id in {author.id for author in db_article.authors}
    if db_article.state == ArticleStates.draft:
        if not (is_editor or is_author):
            raise HTTPException(status_code=403, detail="Access denied")
    elif db_article.state in (ArticleStates.published , ArticleStates.rejected):
        if Roles.moderator not in user.roles:
            raise HTTPException(status_code=403, detail="Access denied")
    elif db_article.state == ArticleStates.approved:
        if Roles.reader not in user.roles:
            raise HTTPException(status_code=403, detail="Access denied")
    return res_article
