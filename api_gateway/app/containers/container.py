from dependency_injector import containers, providers


from app.clients.reroute_request_client import RerouteRequestToServiceClient
from app.config.config import ServicesConfig


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.endpoints.gateway"])

    config = providers.Singleton(
        ServicesConfig.from_json_file,
        "config.json",
    )

    reroute_client = providers.Factory(RerouteRequestToServiceClient, config=config)
