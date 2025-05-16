"""Application module."""

from fastapi import FastAPI

from app.containers.users_container import Container
from app.endpoints.users import users_router


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI()
    app.container = container
    app.include_router(users_router)
    return app


app = create_app()
