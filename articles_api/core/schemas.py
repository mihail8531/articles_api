from typing import List 
from pydantic import BaseModel, EmailStr
from .enums import ArticleStates, Roles


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str


class ArticleBase(BaseModel):
    name: str
    content: str

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    creator_id: int
    state: ArticleStates
    editors_ids: List[int] 
    authors_ids: List[int]


class UserBase(BaseModel):
    email: EmailStr
    username: str
    

class User(UserBase):
    id: int
    is_active: bool
    roles: List[Roles]
    created_articles_ids: List[int]
    editor_for_articles_ids: List[int]
    author_for_aritcles_ids: List[int]


class UserCreate(UserBase):
    password: str



