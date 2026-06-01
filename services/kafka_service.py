import json
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer
from core.config import settings


class KafkaLogger:
    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    @property
    def topic(self) -> str:
        return self._topic

    async def log(self, payload: Dict[str, Any], key: Optional[str] = None) -> None:

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        k = key.encode("utf-8") if key else None
        await self._producer.send_and_wait(self._topic, value=data, key=k)


def kafka_settings() -> dict:
    return {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "topic": settings.KAFKA_LOG_TOPIC,
    }


async def create_kafka_producer() -> AIOKafkaProducer:
    settings = kafka_settings()
    producer = AIOKafkaProducer(bootstrap_servers=settings["bootstrap_servers"])
    await producer.start()
    return producer
