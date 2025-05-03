import json
import logging

from aiokafka import AIOKafkaConsumer

from app.config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaService:

    def __init__(self, kafka_config: KafkaConfig) -> None:
        self.kafka_config = kafka_config
        self.consumer = AIOKafkaConsumer(bootstrap_servers=self.kafka_config.brokers)

    async def consume_message(self):
        consumer = AIOKafkaConsumer(
            self.kafka_config.kafka_topic,
            bootstrap_servers=self.kafka_config.brokers,
            group_id="alexander",
        )
        await consumer.start()
        try:
            async for message in consumer:
                if json.loads(message.value).get("Message") == "Heartbeat":
                    logging.info("Получено heartbeat сообщение")
                    await consumer.commit()
                    continue
                yield json.loads(message.value)

                await consumer.commit()
        finally:
            logging.exception("Kafka consumer был остановлен")
            await consumer.stop()
