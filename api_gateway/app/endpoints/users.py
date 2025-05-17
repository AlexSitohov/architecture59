from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from app.clients.reroute_request_client import (
    RerouteRequestToServiceClient,
)

from fastapi import Request

from app.containers.container import Container

user_router = APIRouter()


@user_router.post("/{service_name}/{path:path}")
@inject
async def logout(
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
