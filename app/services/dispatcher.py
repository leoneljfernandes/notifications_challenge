from app.models.notification import ChannelType
from app.services.email import EmailStrategy
from app.services.push import PushStrategy
from app.services.sms import SMSStrategy


class NotificationDispatcher:
    _strategies = {
        ChannelType.EMAIL: EmailStrategy(),
        ChannelType.SMS: SMSStrategy(),
        ChannelType.PUSH: PushStrategy(),
    }

    @classmethod
    async def dispatch(cls, notification):
        strategy = cls._strategies.get(notification.channel_type)
        if not strategy:
            raise ValueError(f"No strategy found for channel type: {notification.channel_type}")
        await strategy.send(notification)
    