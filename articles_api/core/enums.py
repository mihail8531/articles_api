from enum import Enum


class Roles(Enum):
    admin = "admin"
    moderator = "moderator"
    writer = "writer"
    reader = "reader"

class ArticleStates(Enum):
    draft = "draft"
    published = "published"
    approved = "approved"
    rejected = "rejected"

class CommentaryStates(Enum):
    published = "published"
    approved = "approved"
    rejected = "rejected"
    reject_commentary = "reject_commentary"
