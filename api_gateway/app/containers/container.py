from dependency_injector import containers, providers


from app.clients.reroute_request_client import RerouteRequestToServiceClient
from app.config.config import ServicesConfig
from app.config.config import RedisSettings
from app.repositories.redis_repository import RedisRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.endpoints.gateway",
            "app.endpoints.users",
            "app.utils.cache",
            "app.middleware.jwt_auth_middleware",
        ]
    )

    config = providers.Configuration()

    config.redis.host.from_env("REDIS_HOST", "redis")
    config.redis.port.from_env("REDIS_PORT", 6379)
    config.redis.db.from_env("REDIS_DB", 0)
    config.redis.password.from_env("REDIS_PASSWORD", "")
    config.redis.default_ttl.from_env("REDIS_DEFAULT_TTL", 3600)

    services_config = providers.Singleton(
        ServicesConfig.from_json_file,
        "config.json",
    )

    reroute_client = providers.Factory(
        RerouteRequestToServiceClient, config=services_config
    )

    redis_settings = providers.Factory(
        RedisSettings,
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        default_ttl=config.redis.default_ttl,
    )

    redis_repository = providers.Factory(
        RedisRepository,
        redis_url=redis_settings.provided.url,
    )
