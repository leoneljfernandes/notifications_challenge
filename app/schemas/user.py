from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must include a digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must include an uppercase letter')
        return v

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str

class UserPrivate(UserPublic):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    password: Optional[str] = Field(None, min_length=8)

    @field_validator('password')
    def validate_password(cls, v):
        if v is None:
            return v
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must include a digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must include an uppercase letter')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=255)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=255)