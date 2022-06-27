from typing import Set
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base
from articles_api.core.enums import CommentaryStates, Roles, ArticleStates


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
    commentaries = relationship("Commentary", back_populates="creator")

    def have_role(self, *roles: Roles) -> bool:
        user_roles = {role.role for role in self.roles}
        return bool(set(roles).intersection(user_roles))

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
    commentaries = relationship("Commentary", back_populates="article")

    def is_creator(self, user: User) -> bool:
        return user.id == self.creator_id
    
    def is_author(self, user: User) -> bool:
        return user.id in {author.id for author in self.authors}

    def is_editor(self, user: User) -> bool:
        return user.id in {editor.id for editor in self.editors}
    
    def have_state(self, *states: ArticleStates) -> bool:
        return self.state in states
    
class Commentary(Base):
    __tablename__ = "commentaries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    state = Column(Enum(CommentaryStates))
    creator_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    creator = relationship("User", back_populates="commentaries")
    article = relationship("Article", back_populates="commentaries")

    def is_creator(self, user: User) -> bool:
        return user.id == self.creator_id
    
    def have_state(self, state: CommentaryStates) -> bool:
        return self.state == state

