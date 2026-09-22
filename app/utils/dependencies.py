from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import AsyncSessionLocal

def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.auth import get_current_user
