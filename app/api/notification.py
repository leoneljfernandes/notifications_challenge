from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import create_access_token, verify_password
from app.crud.notification import get_notifications_by_user_id
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token
from app.crud.user import create_user, get_users, get_user, update_user, delete_user, get_user_by_email
from app.database import get_db
from app.auth import get_current_user, get_current_admin
from app.config import settings

router = APIRouter()


@router.get('/my-notifications', response_model=list[NotificationResponse])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = await get_notifications_by_user_id(db, current_user.id)
    return notifications


