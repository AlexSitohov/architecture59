import asyncio
import json
import logging
from typing import Any, Self
import websockets

from aiokafka import AIOKafkaProducer

from config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaService:

    def __init__(self, kafka_config: KafkaConfig) -> None:
        self.kafka_config = kafka_config
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_config.brokers,
            value_serializer=lambda m: json.dumps(m).encode("utf-8"),
        )

    async def send_message(self, message: dict[str, Any]) -> None:
        await self.producer.send(self.kafka_config.kafka_topic, value=message)

    async def start(self) -> None:
        await self.producer.start()
        logger.info("Kafka producer успешно запущен")

    async def stop(self) -> None:
        await self.producer.stop()
        logger.info("Kafka producer успешно остановлен")

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.stop()


async def websocket_client(symbols: list[str]):
    streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
    streams_str = "/".join(streams)
    url = f"wss://fstream.binance.com/stream?streams={streams_str}"
    async with KafkaService(KafkaConfig.provide()) as kafka_service:
        async with websockets.connect(url) as ws:
            while True:
                response = await ws.recv()
                event = json.loads(response)
                await kafka_service.send_message(event)


async def main():
    symbols = [
        "BTCRUB",
        "BTCUSDT",
        "ETHUSDT",
        "ETHRUB",
        "USDTTRCUSDT",
        "USDTTRCRUB",
        "USDTERCUSDT",
        "USDTERCRUB",
    ]
    await websocket_client(symbols)


if __name__ == "__main__":
    asyncio.run(main())
