from typing import Annotated, Optional
import hashlib
from dependency_injector.wiring import inject, Provide
from fastapi import Request, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from app.clients.reroute_request_client import RerouteRequestToServiceClient
from app.containers.container import Container
from app.repositories.redis_repository import RedisRepository


EXCLUDE_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/users_service/login",
    "/users_service/registration",
}


def get_jwt_fingerprint(token: str) -> str:
    """Generate SHA-256 fingerprint for JWT token."""
    return hashlib.sha256(token.encode()).hexdigest()


def extract_bearer_token(auth_header: Optional[str]) -> str:
    """Extract and validate Bearer token from Authorization header."""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return auth_header.split(" ")[1]


async def verify_token_with_service(
    reroute_client: RerouteRequestToServiceClient, request: Request, token: str
) -> bool:
    """Verify token by making request to users service."""
    response = await reroute_client.reroute_request(
        request=request,
        service_name="users_service",
        path="verify_token",
        method="POST",
    )
    return response.status_code == status.HTTP_200_OK


async def cache_token(redis_repo: RedisRepository, token: str, ttl: int = 60) -> None:
    """Cache token in Redis with specified TTL."""
    cache_key = f"jwt:{get_jwt_fingerprint(token)}"
    await redis_repo.set(key=cache_key, value=token, ttl=ttl)


async def is_token_cached(redis_repo: RedisRepository, token: str) -> bool:
    """Check if token exists in cache."""
    cache_key = f"jwt:{get_jwt_fingerprint(token)}"
    return await redis_repo.get(cache_key) is not None


@inject
async def jwt_auth_middleware(
    request: Request,
    call_next,
    reroute_client: Annotated[
        RerouteRequestToServiceClient, Depends(Provide[Container.reroute_client])
    ] = None,
    redis_repository: Annotated[
        RedisRepository, Depends(Provide[Container.redis_repository])
    ] = None,
) -> JSONResponse:
    """JWT authentication middleware with Redis caching."""
    if request.url.path in EXCLUDE_PATHS:
        return await call_next(request)

    try:
        token = extract_bearer_token(request.headers.get("Authorization"))

        if await is_token_cached(redis_repository, token):
            return await call_next(request)

        if not await verify_token_with_service(reroute_client, request, token):
            return JSONResponse(
                content={"message": "Invalid or expired token"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        await cache_token(redis_repository, token)
        return await call_next(request)

    except Exception as e:
        return JSONResponse(
            content={"message": "Authentication failed"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
