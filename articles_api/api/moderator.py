from typing import Literal
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.api.dependencies import (get_draft_article,
                                           get_moderator_or_admin,
                                           get_db, get_published_article,
                                           get_published_commentary)
from articles_api.core import schemas
from articles_api.core.enums import ArticleStates, CommentaryStates
from articles_api.core.mapping import db_article_to_article
from articles_api.db import models, crud

router = APIRouter()

@router.patch("/moderator/{article_id}/approve", response_model=schemas.Article)
def approve_article(db_article: models.Article=Depends(get_published_article),
                    db_user: models.User=Depends(get_moderator_or_admin),
                    db: Session=Depends(get_db)
                    ) -> schemas.Article:
    crud.set_article_state(db, db_article, ArticleStates.approved)
    return db_article_to_article(db_article)

@router.patch("/moderator/{article_id}/reject", response_model=schemas.Article) 
def reject_article(reject_commentary: schemas.CommentaryCreate,
                   db_article: models.Article=Depends(get_published_article),
                   db_user: models.User=Depends(get_moderator_or_admin),
                   db: Session=Depends(get_db)
                   ) -> schemas.Article:
    crud.create_commentary(db, reject_commentary, db_article, db_user, CommentaryStates.reject_commentary)
    crud.set_article_state(db, db_article, ArticleStates.rejected)
    return db_article_to_article(db_article)


@router.patch("/moderator/{commentary_id}/{action}", response_model=schemas.Article)
def approve_or_reject_commentary(action: Literal["approve", "reject"],
                                 db_commentary: models.Commentary=Depends(get_published_commentary),
                                 db_user: models.User=Depends(get_moderator_or_admin),
                                 db: Session=Depends(get_db)
                                 ) -> schemas.Article:
    if action == "approve":
        commentary_state = CommentaryStates.approved
    else:
        commentary_state = CommentaryStates.rejected
    crud.set_commentary_state(db, db_commentary, commentary_state)
    return db_article_to_article(db_commentary)