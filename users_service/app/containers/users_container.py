from dependency_injector import containers, providers

from app.config.jwt_settings import JWTSettings
from app.database.connection import Database
from app.config.database import DatabaseConfig
from app.repositories.users_repository import UsersRepository
from app.services.jwt_service import JWTService
from app.services.users_service import UsersService

from app.repositories.redis_repository import RedisRepository
from app.config.database import RedisSettings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.endpoints.users"])

    config = providers.Configuration()

    config.jwt.key.from_env("SECRET_KEY")
    config.jwt.algorithm.from_env("ALGORITHM")
    config.jwt.token_ttl.from_env("ACCESS_TOKEN_EXPIRE_MINUTES")

    config.redis.host.from_env("REDIS_HOST")
    config.redis.port.from_env("REDIS_PORT")
    config.redis.db.from_env("REDIS_DB")
    config.redis.password.from_env("REDIS_PASSWORD")
    config.redis.default_ttl.from_env("REDIS_DEFAULT_TTL")

    redis_settings = providers.Singleton(
        RedisSettings,
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        default_ttl=config.redis.default_ttl,
    )

    db = providers.Singleton(Database, db_config=DatabaseConfig.provide())

    users_repository = providers.Factory(
        UsersRepository,
        session_factory=db.provided.session,
    )

    redis_repository = providers.Factory(
        RedisRepository,
        redis_url=redis_settings.provided.url,
    )

    jwt_setting = providers.Singleton(
        JWTSettings,
        key=config.jwt.key,
        algorithm=config.jwt.algorithm,
        token_ttl=config.jwt.token_ttl,
    )

    jwt_service = providers.Factory(JWTService, jwt_config=jwt_setting)

    users_service = providers.Factory(
        UsersService,
        users_repository=users_repository,
        jwt_service=jwt_service,
        redis_repository=redis_repository,
    )
