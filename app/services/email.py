
from app.models import notification

from .channel import ChannelStrategy

class EmailStrategy(ChannelStrategy):
    async def send(self, notification: notification.Notification):
        print("Validating destination...")

        email_address = notification.user.email

        if email_address is None or not isinstance(email_address, str) or "@" not in email_address:
            raise ValueError("Invalid email address provided.")

        print("Preparing message...")
        
        print(f"Sending email to {email_address} with title: {notification.title} and message: {notification.message}")