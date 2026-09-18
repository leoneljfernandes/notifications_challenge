from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.auth import get_current_user, get_current_admin_user
