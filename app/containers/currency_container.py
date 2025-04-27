from dependency_injector import containers, providers

from app.database.connection import Database
from app.config.database import DatabaseConfig
from app.repositories.currency_repository import CurrencyRepository
from app.services.currency_service import CurrencyService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.endpoints.currency"])

    db = providers.Singleton(Database, db_config=DatabaseConfig.provide())

    currency_repository = providers.Factory(
        CurrencyRepository,
        session_factory=db.provided.session,
    )

    currency_service = providers.Factory(
        CurrencyService,
        currency_repository=currency_repository,
    )
