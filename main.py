from fastapi import FastAPI, Request
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from api.route import router as city_route
import redis.asyncio as redis
from aiokafka import AIOKafkaProducer
from core.config import settings
from services.cache_service import CityCountryCodeCache, cache_config
from services.kafka_service import KafkaLogger

REDIS_URL = settings.REDIS_URL
KAFKA_SERVERS = settings.KAFKA_BOOTSTRAP_SERVERS


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        f"Server started at {datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S')}"
    )
  
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    app.state.redis = redis_client
    
    app.state.city_cache = CityCountryCodeCache(
        client=redis_client, config=cache_config()
    )

    await app.state.redis.ping()
    
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVERS)
    await producer.start()
    app.state.kafka_producer = producer
    
    app.state.kafka_logger = KafkaLogger(producer=producer, topic="app_logs")

    yield

    
    await producer.stop()
    await app.state.redis.close()
    print(
        f"Server shutdown at {datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S')}"
    )


app = FastAPI(
    title="Mohaymen test API",
    version="0.0.1",
    contact={
        "name": "Hossein",
        "email": "hossein@hossein.com",
        "url": "https://github.com/hosseinpk/mohaymen_test.git",
    },
    lifespan=lifespan,
)


app.include_router(city_route, prefix="/api")


@app.get("/health", summary="health check")
async def health_check():
    return {"status": "ok", "datetime": datetime.now(timezone.utc).isoformat()}
