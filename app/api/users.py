from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import create_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token
from app.crud.user import create_user, get_users, get_user, update_user, delete_user, get_user_by_email
from app.database import get_db
from app.auth import get_current_user, get_current_admin
from app.config import settings

router = APIRouter()

@router.get('/', response_model=list[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, 
                     db: AsyncSession = Depends(get_db),
                     admin_user: User = Depends(get_current_admin)):
    return await get_users(db, skip=skip, limit=limit)

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail='Email already registered')

    return await create_user(db, user)

@router.get('/{user_id}', response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@router.put('/{user_id}', response_model=UserResponse)
async def modify_user(user_id: int, user: UserUpdate, 
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this user",
        )

    result =await update_user(db, user_id, user)

    if result is None:
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to update this user",
                )

    return result


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this user",
        )

    await delete_user(db, user_id)
    return None

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), 
                                 db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
