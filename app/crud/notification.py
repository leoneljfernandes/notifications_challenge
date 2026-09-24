from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate


async def get_notification_by_id(db: AsyncSession, notification_id: int):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    return result.scalar_one_or_none()

async def get_notifications_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Notification).where(Notification.user_id == user_id))
    return result.scalars().all()


async def create_notification(db: AsyncSession, notification: NotificationCreate, user_id: int):

    db_notification = Notification(
        title=notification.title,
        message=notification.message,
        user_id=user_id,
        channel_type=notification.channel_type,
        channel_metadata=notification.channel_metadata
    )

    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

async def update_notification(db: AsyncSession, notification_id: int, updated_notification: NotificationUpdate):
    notification = await get_notification_by_id(db, notification_id)
    if not notification:
        return None

    updated_data = updated_notification.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(notification, key, value)

    await db.commit()
    await db.refresh(notification)
    return notification

async def delete_notification(db: AsyncSession, notification_id: int):
    notification = await get_notification_by_id(db, notification_id)
    if not notification:
        return None
    await db.delete(notification)
    await db.commit()
    return notification

