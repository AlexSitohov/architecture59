from fastapi import FastAPI

from app.containers.container import Container
from app.endpoints.gateway import gateway_router
from app.middleware.jwt_auth_middleware import jwt_auth_middleware


def create_app() -> FastAPI:
    container = Container()
    container.init_resources()
    app = FastAPI()
    app.container = container
    app.middleware("http")(jwt_auth_middleware)
    app.include_router(gateway_router)
    return app


app = create_app()
