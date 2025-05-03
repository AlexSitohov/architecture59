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


@dataclass
class DatabaseConfig:
    db_login: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    echo: bool
    pool_size: int

    @classmethod
    def provide(cls) -> Self:
        return cls(
            db_login=os.environ["CLICKHOUSE_USER"],
            db_password=os.environ["CLICKHOUSE_PASSWORD"],
            db_host=os.environ["CLICKHOUSE_HOST"],
            db_port=int(os.environ["CLICKHOUSE_PORT"]),
            db_name=os.environ["CLICKHOUSE_DB"],
            echo=False,
            pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", 10)),
        )
