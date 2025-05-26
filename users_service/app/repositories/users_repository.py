from fastapi import HTTPException, status
from sqlalchemy import select, insert, text
from sqlalchemy.ext.asyncio import async_sessionmaker
from passlib.context import CryptContext

from app.models.users import UserCreate, UserResponse, UserConfirm
from app.tables.users import User, UserConfirmedStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self.session = session_factory

    async def create_user(self, dto: UserCreate, verification_code: str):
        hashed_password = pwd_context.hash(dto.password)

        async with self.session() as session:
            try:
                stmt = (
                    insert(UserConfirmedStatus)
                    .values(
                        email=dto.email,
                        password_hash=hashed_password,
                        verification_code=verification_code,
                    )
                    .returning(UserConfirmedStatus)
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

    async def confirm_email(self, dto: UserConfirm):
        async with self.session() as session:
            query = select(UserConfirmedStatus).where(
                UserConfirmedStatus.email == dto.email
            )
            result = await session.execute(query)
            user = result.scalars().one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            if dto.code != user.verification_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code",
                )
            insert_query = text(
                """
                INSERT INTO users (email, password_hash)
                SELECT email, password_hash
                FROM users_confirmed_status
                WHERE email = :email
            """
            )
            await session.execute(insert_query, {"email": dto.email})

            delete_query = text(
                """
                DELETE FROM users_confirmed_status
                WHERE email = :email
            """
            )
            await session.execute(delete_query, {"email": dto.email})

            await session.commit()

            return {"email": dto.email, "confirmed": True}
