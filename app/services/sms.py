from .channel import ChannelStrategy
from app.models.notification import Notification


class SMSStrategy(ChannelStrategy):
    async def send(self, notification: Notification):
        
        print("Validating destination...")

        phone_number = notification.channel_metadata.get('phone_number')

        print("Preparing message...")

        if phone_number is None or not isinstance(phone_number, str) or not phone_number.isdigit():
            raise ValueError("Invalid phone number provided.")

        if len(notification.message) > 160:
            raise ValueError("Message exceeds 160 characters.")
        print(f"Sending SMS to {phone_number} with message: {notification.message}")