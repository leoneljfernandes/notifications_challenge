from fastapi import APIRouter

api_router = APIRouter()

from app.api import users

api_router.include_router(users.router, prefix='/users', tags=['users'])

