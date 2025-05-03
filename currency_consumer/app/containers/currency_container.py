from dependency_injector import containers, providers

from app.config import KafkaConfig
from app.database.connection import Database
from app.config import DatabaseConfig
from app.kafka_service.kafka_service import KafkaService
from app.repositories.currency_repository import CurrencyRepository

from app.services.currency_service import CurrencyService


class Container(containers.DeclarativeContainer):
    db = providers.Singleton(Database, db_config=DatabaseConfig.provide())

    currency_repository = providers.Factory(
        CurrencyRepository,
        session_factory=db.provided.session,
    )

    kafka_service = providers.Factory(
        KafkaService,
        kafka_config=KafkaConfig.provide(),
    )

    currency_service = providers.Factory(
        CurrencyService,
        currency_repository=currency_repository,
        kafka_service=kafka_service,
    )
