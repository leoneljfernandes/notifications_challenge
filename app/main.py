from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import api_router
from app.database import engine as db_engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arrancamos la base de datos de forma asíncrona
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    
app = FastAPI(lifespan=lifespan)


app.include_router(api_router, prefix='/api')

@app.get('/')
def root():
    return {'message': 'Enhanced FastAPI App'}
