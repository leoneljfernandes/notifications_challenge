from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.notification import get_notification_by_id, get_notifications_by_user_id
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.user import UserResponse
from app.database import get_db
from app.auth import get_current_user, get_current_admin
from app.config import settings
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.services.dispatcher import NotificationDispatcher
from app.crud.notification import create_notification, update_notification, delete_notification

router = APIRouter()


@router.get('/my-notifications', response_model=list[NotificationResponse])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = await get_notifications_by_user_id(db, current_user.id)
    return notifications


@router.post('/create-notification', response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def post_new_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_notif = await create_notification(db, notification, current_user.id)

    await NotificationDispatcher.dispatch(db_notif)
    return db_notif


@router.put('/update-notification/{notification_id}', response_model=NotificationResponse)
async def update_a_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_notification = await get_notification_by_id(db, notification_id)
    if not existing_notification:
        raise HTTPException(status_code=404, detail='Notification not found')

    if existing_notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this notification",
        )

    updated_notification = await update_notification(db, notification_id, notification)
    if updated_notification is None:
        raise HTTPException(status_code=404, detail='Notification not found')
    return updated_notification    

@router.delete('/delete-notification/{notification_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = await get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail='Notification not found')


    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this notification",
        )

    await delete_notification(db, notification_id)