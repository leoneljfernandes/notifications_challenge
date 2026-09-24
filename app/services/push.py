from .channel import ChannelStrategy
from app.models.notification import Notification

class PushStrategy(ChannelStrategy):
    async def send(self, notification: Notification):
        print("Validating destination...")
        print("Preparing message...")
        
        print(f"Sending push notification to {notification.channel_metadata.get('device_token')} with title: {notification.title} and message: {notification.message}")