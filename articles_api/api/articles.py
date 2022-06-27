from typing import List, Literal
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.api.dependencies import (RolesChecker, get_approved_article, get_current_active_user,
                                           get_db, get_article, get_db_user, get_draft_article,
                                           get_writer_or_admin, get_reader_or_admin,
                                           get_writer_moderator_or_admin)
from articles_api.core.enums import ArticleStates, CommentaryStates, Roles
from articles_api.core.mapping import db_article_to_article
from articles_api.db import crud
from articles_api.core import schemas
from articles_api.db import models


router = APIRouter()

@router.post("/articles/create", response_model=schemas.Article)
def create_article(article_create: schemas.ArticleCreate,
                   db_user: models.User = Depends(get_writer_or_admin),
                   db: Session = Depends(get_db)
                   ) -> schemas.Article:
    db_aritcle = crud.create_article(db, article_create, db_user)
    return db_article_to_article(db_aritcle)

@router.get("/articles/my_created_articles", response_model=List[int])
def get_my_created_articles_ids(db_user: models.User = Depends(get_current_active_user),
                                db: Session = Depends(get_db)
                                ) -> List[int]:
    return [article.id for article in db_user.created_articles]

@router.get("/articles/my_edited_articles", response_model=List[int])
def get_my_edited_articles_ids(db_user: models.User = Depends(get_current_active_user),
                               db: Session = Depends(get_db)
                               ) -> List[int]:
    return [article.id for article in db_user.editor_for_articles]

@router.get("/articles/my_authored_articles", response_model=List[int])
def get_my_authored_articles_ids(db_user: models.User = Depends(get_current_active_user),
                                 db: Session = Depends(get_db)
                                 ) -> List[int]:
    return [article.id for article in db_user.author_for_articles]

@router.get("/articles/approved_articles_ids", response_model=List[int])
def get_approved_articles_ids(db_user: models.User = Depends(get_reader_or_admin),
                              db: Session = Depends(get_db)
                              ) -> List[int]:
    return [article.id for article in crud.get_articles_by_state(db, ArticleStates.approved)]

@router.get("/articles/published_articles_ids", response_model=List[int])
def get_published_articles_ids(user: models.User = Depends(get_writer_moderator_or_admin),
                               db: Session = Depends(get_db)
                               ) -> List[int]:
    if not user.have_one_of_roles({Roles.moderator, Roles.admin}):
        return [article.id for article in crud.get_articles_by_author(db, user)
                if article.state == ArticleStates.published]
    return [article.id for article in crud.get_articles_by_state(db, ArticleStates.published)]

@router.patch("/articles/{article_id}/create_commentary", response_model=schemas.Commentary)
def create_commentary(commentary: schemas.CommentaryCreate,
                      db_article: models.Article = Depends(get_approved_article),
                      db_user: models.User = Depends(get_reader_or_admin),
                      db: Session = Depends(get_db)
                      ) -> models.Commentary:
    db_commentary = crud.create_commentary(db, commentary, db_article, db_user, CommentaryStates.published)
    return db_commentary # without mapping because orm_mode 


@router.patch("/articles/{article_id}/edit", response_model=schemas.Article) 
def edit_article(article: schemas.ArticleCreate,
                 db_article: models.Article = Depends(get_draft_article),
                 db_user: models.User = Depends(get_writer_or_admin),
                 db: Session = Depends(get_db)
                 ) -> schemas.Article:
    is_creator = db_article.is_creator(db_user)
    is_editor = db_article.is_editor(db_user)
    is_author = db_article.is_author(db_user)
    if not (is_creator or is_editor or is_author):
        raise HTTPException(status_code=403, detail="Access denied")
    crud.edit_article(db, db_article, article)
    return db_article_to_article(db_article)

@router.patch("/articles/{article_id}/publish", response_model=schemas.Article)
def publish_article(db_article: models.Article = Depends(get_draft_article),
                    db_user: models.User = Depends(get_writer_or_admin),
                    db: Session = Depends(get_db)
                    ) -> schemas.Article:
    if not db_article.is_creator(db_user):
        raise HTTPException(status_code=403, detail="Access denied")
    crud.set_article_state(db, db_article, ArticleStates.published) 
    return db_article_to_article(db_article)

@router.patch("/articles/{article_id}/unpublish", response_model=schemas.Article)
def unpublish_article(db_article: models.Article = Depends(get_article),
                      db_user: models.User = Depends(get_writer_or_admin),
                      db: Session = Depends(get_db)
                      ) -> schemas.Article:
    if not db_article.is_creator(db_user):
        raise HTTPException(status_code=403, detail="Access denied")
    crud.set_article_state(db, db_article, ArticleStates.draft) 
    return db_article_to_article(db_article)

@router.patch("/articles/{article_id}/{action}/author", response_model=schemas.Article) 
def add_or_remove_author(action: Literal["add", "remove"],
                         db_author: models.User = Depends(get_db_user),
                         db_article: models.Article = Depends(get_draft_article),
                         db_user: models.User = Depends(get_writer_or_admin),
                         db: Session = Depends(get_db)
                         ) -> schemas.Article:
    if not db_article.is_creator(db_user):
        raise HTTPException(status_code=403, detail="Access denied")
    is_author = db_article.is_author(db_author)
    if action == "add":
        if is_author:
            raise HTTPException(status_code=409, detail="Given user already an author")
        crud.add_article_author(db, db_article, db_author.id)
    elif action == "remove":
        if not is_author:
            raise HTTPException(status_code=409, detail="Given user is not an author")
        crud.remove_article_author(db, db_article, db_author.id)
    return db_article_to_article(db_article)


@router.patch("/articles/{article_id}/{action}/editor", response_model=schemas.Article) 
def add_or_remove_editor(action: Literal["add", "remove"],
                         db_editor: models.User = Depends(get_db_user),
                         db_article: models.Article = Depends(get_draft_article),
                         db_user: models.User = Depends(get_writer_or_admin),
                         db: Session = Depends(get_db)
                         ) -> schemas.Article:
    if not db_article.is_creator(db_user):
        raise HTTPException(status_code=403, detail="Access denied")
    is_editor = db_article.is_editor(db_editor)
    if action == "add":
        if is_editor:
            raise HTTPException(status_code=409, detail="Given user already an editor")
        crud.add_article_editor(db, db_article, db_editor.id)
    elif action == "remove":
        if not is_editor:
            raise HTTPException(status_code=409, detail="Given user is not an editor")
        crud.remove_article_editor(db, db_article, db_editor.id)
    return db_article_to_article(db_article)


@router.get("/articles/{article_id}", response_model=schemas.Article)
def get_aritcle(db_article: models.Article = Depends(get_article),
                db_user: models.User = Depends(get_current_active_user)
                ) -> schemas.Article:
    res_article = db_article_to_article(db_article)
    is_creator = db_article.is_creator(db_user)
    is_admin = db_user.have_role(Roles.admin)
    if is_creator or is_admin:
        return res_article
    is_editor = db_article.is_editor(db_user)
    is_author = db_article.is_author(db_user)
    if db_article.have_state(ArticleStates.draft):
        if not (is_editor or is_author):
            raise HTTPException(status_code=403, detail="Access denied")
    elif db_article.have_state(ArticleStates.published, ArticleStates.rejected):
        if not db_user.have_role(Roles.moderator):
            raise HTTPException(status_code=403, detail="Access denied")
    elif db_article.have_state(ArticleStates.approved):
        if not db_user.have_role(Roles.reader):
            raise HTTPException(status_code=403, detail="Access denied")
    return res_article
