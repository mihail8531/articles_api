from fastapi import APIRouter

from articles_api.api import login, users

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
