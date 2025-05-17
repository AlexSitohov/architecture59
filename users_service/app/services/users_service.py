from app.models.users import UserCreate, VerifyToken
from app.repositories.users_repository import UsersRepository
from app.repositories.redis_repository import RedisRepository
from app.services.jwt_service import JWTService


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
        return await self.users_repository.create_user(dto)

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
