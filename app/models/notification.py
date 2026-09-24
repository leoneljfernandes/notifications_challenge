from datetime import datetime, UTC

from sqlalchemy import Column, Enum, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models import Base
from app.models.user import User
import enum
from sqlalchemy import JSON

class ChannelType(str,enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    channel_type = Column(Enum(ChannelType), nullable=False)
    channel_metadata = Column(JSON, default={})

    user: Mapped[User] = relationship("User", back_populates="notifications", lazy="selectin")




