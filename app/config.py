from pydantic import SecretStr
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "mi_base_de_datos")

    # Si necesitas volver temporalmente a SQLite, puedes alternar aquí:
    DATABASE_URL: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    secret_key: SecretStr = os.getenv("SECRET_KEY")
    
    algorithm: str = 'HS256'

    access_token_expire_minutes: int = 30

    class Config:
        env_file = '.env'

settings = Settings()
