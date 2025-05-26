from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException
from dependency_injector.wiring import inject, Provide

from app.containers.users_container import Container
from app.models.users import UserCreate, UserResponse, UserConfirm
from app.services.users_service import UsersService

users_router = APIRouter(tags=["USERS"], prefix="/api/v1")


@users_router.post("/registration", status_code=200, response_model=UserResponse)
@inject
async def registration(
    dto: UserCreate,
    users_service: Annotated[UsersService, Depends(Provide[Container.users_service])],
):
    return await users_service.create_user(dto)


@users_router.post("/confirm_email", status_code=200)
@inject
async def confirm_email(
    dto: UserConfirm,
    users_service: Annotated[UsersService, Depends(Provide[Container.users_service])],
):
    return await users_service.confirm_email(dto)


@users_router.post("/login", status_code=200)
@inject
async def login(
    dto: UserCreate,
    users_service: Annotated[UsersService, Depends(Provide[Container.users_service])],
) -> str:
    return await users_service.login(dto)


async def get_token_from_header(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=400, detail="Authorization header must start with Bearer"
        )
    return authorization[7:]


@users_router.post("/verify_token", status_code=200)
@inject
async def verify_token(
    users_service: Annotated[UsersService, Depends(Provide[Container.users_service])],
    token: str = Depends(get_token_from_header),
) -> dict:
    return await users_service.verify_token(token)


@users_router.post("/logout", status_code=200)
@inject
async def logout(
    users_service: Annotated[UsersService, Depends(Provide[Container.users_service])],
    token: str = Depends(get_token_from_header),
) -> str:
    return await users_service.logout(token)
