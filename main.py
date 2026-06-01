from fastapi import FastAPI,Request
from datetime import datetime,timezone
from contextlib import asynccontextmanager
from api.route import router as city_route
import redis.asyncio as redis
from core.config import settings

REDIS_URL = settings.REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.from_url(REDIS_URL, decode_responses=True)
    print(f" Server started at {datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S')}")
    await app.state.redis.ping()
    yield
    await app.state.redis.close()
    print(f" Server shutdown at {datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S')}")

app = FastAPI(
    title="Mohaymen test API",
    version="0.0.1",
    contact={
        "name": "Hossein",
        "email": "hossein@hossein.com",
        "url": "https://github.com/hosseinpk/mohaymen_test.git"
    },
    lifespan=lifespan,
)


app.include_router(city_route, prefix="/api")


@app.get("/health",summary="health check")
async def health_check():
    return {"status":"ok","datetime":datetime.now(timezone.utc).isoformat()}
