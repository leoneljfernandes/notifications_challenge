from abc import ABC, abstractmethod

from app.models.notification import Notification


class ChannelStrategy:
    
    @abstractmethod
    async def send(self, notification: Notification):
       pass        

