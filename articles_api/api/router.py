from fastapi import APIRouter

from articles_api.api import login, users, articles, admin, moderator, commentaries

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(articles.router)
api_router.include_router(admin.router)
api_router.include_router(moderator.router)
api_router.include_router(commentaries.router)
