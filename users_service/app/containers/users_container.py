from dependency_injector import containers, providers
from app.config.jwt_settings import JWTSettings
from app.database.connection import Database
from app.config.database import DatabaseConfig
from app.repositories.users_repository import UsersRepository
from app.services.jwt_service import JWTService
from app.services.users_service import UsersService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.endpoints.users"])

    config = providers.Configuration()

    config.jwt.key.from_env("SECRET_KEY")
    config.jwt.algorithm.from_env("ALGORITHM")
    config.jwt.token_ttl.from_env("ACCESS_TOKEN_EXPIRE_MINUTES")

    db = providers.Singleton(Database, db_config=DatabaseConfig.provide())

    users_repository = providers.Factory(
        UsersRepository,
        session_factory=db.provided.session,
    )

    jwt_setting = providers.Singleton(
        JWTSettings,
        key=config.jwt.key,
        algorithm=config.jwt.algorithm,
        token_ttl=config.jwt.token_ttl,
    )

    jwt_service = providers.Factory(JWTService, jwt_config=jwt_setting)

    currency_service = providers.Factory(
        UsersService,
        users_repository=users_repository,
        jwt_service=jwt_service,
    )
