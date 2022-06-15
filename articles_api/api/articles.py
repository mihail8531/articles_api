from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from articles_api.api.dependencies import get_db, get_writer_or_admin, get_reader_or_admin
from articles_api.core.enums import Roles
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

@router.get("/articles/{article_id}", response_model=Article)
def get_aritcle(article_id: int, user: models.User = Depends(get_reader_or_admin)) -> Article:
    pass
