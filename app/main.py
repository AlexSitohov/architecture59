"""Application module."""

from fastapi import FastAPI

from app.containers.currency_container import Container
from app.endpoints.currency import currency_router


class APP:
    pass


def create_app() -> FastAPI:
    container = Container()

    db = container.db()
    db.create_database()

    app = FastAPI()
    app.container = container
    app.include_router(currency_router)
    return app


app = create_app()
