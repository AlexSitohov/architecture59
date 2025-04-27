from typing import Annotated
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.containers.currency_container import Container
from app.services.currency_service import CurrencyService

currency_router = APIRouter(tags=["CURRENCY"], prefix="/api/v1")


@currency_router.get("/currency")
@inject
async def get_stable_currency_rate(
    currency_service: Annotated[
        CurrencyService, Depends(Provide[Container.currency_service])
    ],
):
    return await currency_service.get_stable_currency_rate()
