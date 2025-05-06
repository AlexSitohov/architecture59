from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from app.clients.reroute_request_client import (
    RerouteRequestToServiceClient,
)

from fastapi import Request

from app.containers.container import Container

gateway_router = APIRouter()


@gateway_router.api_route(
    "/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@inject
async def gateway(
    request: Request,
    service_name: str,
    path: str,
    reroute_client: Annotated[
        RerouteRequestToServiceClient, Depends(Provide[Container.reroute_client])
    ],
):

    return await reroute_client.reroute_request(
        request=request, service_name=service_name, path=path
    )
