from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base
from articles_api.core.enums import Roles, ArticleStates

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    editor_for_articles = relationship("Article", secondary="editor_articles", back_populates="editors")
    author_for_articles = relationship("Article", secondary="author_articles", back_populates="authors")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role = Enum(Roles)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="roles")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    content = Column(Text)
    state = Enum(ArticleStates)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_articles")
    editors = relationship("User", secondary="editor_aritcles", back_populates="editor_for_articles")
    authors = relationship("User", secondary="author_aritcles", back_populates="author_for_articles")


class EditorArticle(Base):
    __tablename__ = "editor_articles"

    id = Column(Integer, primary_key=True, index=True)
    editor_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey("articles.id"))


class AuthorArticle(Base):
    __tablename__ = "author_articles"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey("articles.id"))