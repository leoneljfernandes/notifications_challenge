from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)
    channel_type: str = Field(..., min_length=1, max_length=50)
    channel_metadata: Optional[dict] = Field(default={})

    @field_validator('channel_type')
    def validate_channel_type(cls, v):
        if v not in ['email', 'push', 'sms']:
            raise ValueError('Invalid channel type. Must be "email" or "push" or "sms".')
        return v

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    message: Optional[str] = Field(None, min_length=1, max_length=500)
    channel_type: Optional[str] = Field(None, min_length=1, max_length=50)
    channel_metadata: Optional[dict] = Field(default=None)

    @field_validator('channel_type')
    def validate_channel_type(cls, v):
        if v is not None and v not in ['email', 'push', 'sms']:
            raise ValueError('Invalid channel type. Must be "email" or "push" or "sms".')
        return v

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    channel_type: str
    channel_metadata: Optional[dict]
