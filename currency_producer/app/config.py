from dataclasses import dataclass
import os
from typing import Self


@dataclass
class KafkaConfig:
    kafka_topic: str
    brokers: str

    @classmethod
    def provide(cls) -> Self:
        return cls(
            kafka_topic=os.environ.get("KAFKA_TOPIC"),
            brokers=os.environ.get("BROKERS"),
        )
