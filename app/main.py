from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from app.api import api_router
from app.database import engine as db_engine
from app.models import Base
from app.api.notification import router as notification_router
from app.telemetry import setup_telemetry



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arrancamos la base de datos de forma asíncrona
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    
app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app, endpoint='/metrics')
setup_telemetry(app, db_engine)


app.include_router(api_router, prefix='/api')
app.include_router(notification_router, prefix='/api/notifications', tags=['Notifications'])


@app.get('/')
def root():
    return {'message': 'Enhanced FastAPI App'}



