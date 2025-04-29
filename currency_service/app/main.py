"""Application module."""

from fastapi import FastAPI

from app.containers.currency_container import Container
from app.endpoints.currency import currency_router


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI()
    app.container = container
    app.include_router(currency_router)
    return app


app = create_app()
