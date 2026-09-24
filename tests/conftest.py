import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import get_db
from app.models import Base

# Usaremos una base de datos en archivo local solo para las pruebas, 
# para poder compartirla fácilmente entre SQLAlchemy síncrono (setup) y asíncrono (app)
TEST_DB_URL_SYNC = "sqlite:///./test_notifications.db"
TEST_DB_URL_ASYNC = "sqlite+aiosqlite:///./test_notifications.db"

# Motor síncrono para crear y destruir tablas rápidamente en los fixtures
sync_engine = create_engine(TEST_DB_URL_SYNC, connect_args={"check_same_thread": False})

# Motor asíncrono para inyectar a la app de FastAPI
async_engine = create_async_engine(TEST_DB_URL_ASYNC, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """
    Patrón Clean-Execute-Clean.
    Se ejecuta antes y después de CADA test automáticamente.
    """
    # 1. Clean (por si quedó algo de una corrida anterior fallida)
    Base.metadata.drop_all(bind=sync_engine)
    # 2. Setup (Crear tablas limpias)
    Base.metadata.create_all(bind=sync_engine)
    
    yield # Aquí se ejecuta el test
    
    # 3. Clean (Borrar todo al terminar)
    Base.metadata.drop_all(bind=sync_engine)

@pytest.fixture(scope="function")
def client():
    """
    Fixture que inyecta nuestra base de datos de test en lugar de Postgres.
    """
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
            
    # Hacemos override de la dependencia
    app.dependency_overrides[get_db] = override_get_db
    
    # Parcheamos el engine global de main.py para que el evento 'lifespan' 
    # de FastAPI al iniciar el TestClient no intente conectarse a Postgres.
    import sys
    sys.modules['app.main'].db_engine = async_engine
    
    # Entregamos el cliente HTTP simulado atrapando los errores 500
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
        
    # Limpiamos el override
    app.dependency_overrides.clear()

