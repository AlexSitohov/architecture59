from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from passlib.context import CryptContext

from app.models.users import UserCreate, UserResponse
from app.tables.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self.session = session_factory

    async def create_user(self, dto: UserCreate):
        hashed_password = pwd_context.hash(dto.password)

        async with self.session() as session:
            try:
                stmt = (
                    insert(User)
                    .values(email=dto.email, password_hash=hashed_password)
                    .returning(User)
                )
                result = await session.execute(stmt)
                user = result.scalars().one()
                await session.commit()
                return user

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected error during user creation {e}",
                )

    async def check_user_validity(self, dto: UserCreate) -> dict:
        async with self.session() as session:
            try:
                query = select(User).where(User.email == dto.email)
                result = await session.execute(query)
                user = result.scalars().one_or_none()

                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )

                if not self._verify_password(dto.password, user.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid password",
                    )

                user_dict = UserResponse.model_validate(user).model_dump(
                    exclude={"password_hash"}
                )
                return user_dict

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected error during login {e}",
                )

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password hash format",
            )
