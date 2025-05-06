from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

from app.config.config import ServicesConfig


class RerouteRequestToServiceClient:
    def __init__(self, config: ServicesConfig):
        self.__global_config = config

    async def reroute_request(self, request: Request, service_name: str, path: str):
        target_url = self.__construct_url(service_name, path)
        async with httpx.AsyncClient() as client:
            try:
                headers = dict(request.headers)
                headers.pop("host", None)
                headers.pop("content-length", None)
                body = await request.body()
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                    timeout=10.0,
                )

                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            except httpx.ConnectError:
                raise HTTPException(status_code=502, detail="Service connection error")
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")

    def __construct_url(self, service_name: str, path: str):
        config = self.__global_config.get_service_config(service_name)
        return f"{config.base_url}{config.prefix}/{path}"
