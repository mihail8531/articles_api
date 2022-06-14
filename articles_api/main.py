import imp
from fastapi import FastAPI
import secrets
from .api.router import api_router
from .config import config



app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.DESCRIPTION
)

app.include_router(api_router)