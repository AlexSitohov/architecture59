import random

from app.models.users import UserCreate, UserConfirm
from app.repositories.users_repository import UsersRepository
from app.repositories.redis_repository import RedisRepository
from app.services.jwt_service import JWTService
from app.celery.send_email import send_verification_email


class UsersService:

    def __init__(
        self,
        users_repository: UsersRepository,
        jwt_service: JWTService,
        redis_repository: RedisRepository,
    ):
        self.users_repository = users_repository
        self.jwt_service = jwt_service
        self.redis_repository = redis_repository

    async def create_user(self, dto: UserCreate):
        verification_code = self.__verification_code
        send_verification_email.delay(dto.email, verification_code)
        return await self.users_repository.create_user(dto, verification_code)

    async def login(self, dto: UserCreate):
        user_data = await self.users_repository.check_user_validity(dto)
        token = self.jwt_service.create_access_token(user_data)
        await self.redis_repository.cache_jwt_token(token)
        return token

    async def logout(self, token: str):
        await self.redis_repository.blacklist_jwt_token(token)
        await self.redis_repository.delete_cached_jwt_token(token)
        return token

    async def verify_token(self, token: str):
        return self.jwt_service.verify_access_token(token)

    async def confirm_email(
        self,
        dto: UserConfirm,
    ):
        return await self.users_repository.confirm_email(dto)

    @property
    def __verification_code(self) -> str:
        return f"{random.randint(0, 999999):06d}"
