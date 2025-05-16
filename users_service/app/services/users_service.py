from app.models.users import UserCreate, VerifyToken
from app.repositories.users_repository import UsersRepository
from app.services.jwt_service import JWTService


class UsersService:
    def __init__(self, users_repository: UsersRepository, jwt_service: JWTService):
        self.users_repository = users_repository
        self.jwt_service = jwt_service

    async def create_user(self, dto: UserCreate):
        return await self.users_repository.create_user(dto)

    async def login(self, dto: UserCreate):
        user_data = await self.users_repository.check_user_validity(dto)
        return self.jwt_service.create_access_token(user_data)

    async def verify_token(self, token: str):
        return self.jwt_service.verify_access_token(token)
