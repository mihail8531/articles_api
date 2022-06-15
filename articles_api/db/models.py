from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base
from articles_api.core.enums import Roles, ArticleStates


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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_articles = relationship("Article", back_populates="creator")
    editor_for_articles = relationship("Article",
                                       secondary=EditorArticle.__table__,
                                       back_populates="editors")
    author_for_articles = relationship("Article",
                                       secondary=AuthorArticle.__table__,
                                       back_populates="authors")
    roles = relationship("Role", back_populates="owner")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(Roles))
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="roles")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    content = Column(Text)
    state = Column(Enum(ArticleStates))
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_articles")
    editors = relationship("User", secondary=EditorArticle.__table__,
                           back_populates="editor_for_articles")
    authors = relationship("User", secondary=AuthorArticle.__table__,
                           back_populates="author_for_articles")

