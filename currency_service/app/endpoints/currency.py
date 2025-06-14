from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException
from dependency_injector.wiring import inject, Provide
from jose import jwt, JWTError

from app.containers.currency_container import Container
from app.models.currency import CurrencyGET, CurrencySubscription
from app.services.currency_service import CurrencyService

currency_router = APIRouter(tags=["CURRENCY"], prefix="/api/v1")


async def get_token_from_header(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=400, detail="Заголовок Authorization должен начинаться с Bearer"
        )
    return authorization[7:]


async def decode_jwt(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(
            token,
            "",
            options={"verify_signature": False},
            algorithms=["HS256"],
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Невозможно декодировать токен")


@currency_router.get("/currency", status_code=200, response_model=list[CurrencyGET])
@inject
async def get_stable_currency_rate(
    currency_service: Annotated[
        CurrencyService, Depends(Provide[Container.currency_service])
    ],
    user_data: dict = Depends(decode_jwt),
):
    return await currency_service.get_stable_currency_rate(user_data)


@currency_router.post("/currency_subscription", status_code=201)
@inject
async def create_currency_subscription(
    currency_service: Annotated[
        CurrencyService, Depends(Provide[Container.currency_service])
    ],
    dto: CurrencySubscription,
    user_data: dict = Depends(decode_jwt),
):
    return await currency_service.create_currency_subscription(dto, user_data)
