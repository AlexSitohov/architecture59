import logging
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    async_scoped_session,
)

from sqlalchemy.engine import URL

from app.config.database import DatabaseConfig

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_config: DatabaseConfig) -> None:

        self._session_context = ContextVar("session_context")

        self.__uri = self.__construct_url(db_config)
        self.__engine = create_async_engine(
            url=self.__uri,
            echo=db_config.echo,
            pool_size=db_config.pool_size,
            future=True,
        )
        self.__session_factory = async_scoped_session(
            async_sessionmaker(
                self.__engine, expire_on_commit=False, class_=AsyncSession
            ),
            scopefunc=self._session_context.get,  # Добавляем scopefunc
        )

    @staticmethod
    def __construct_url(db_config: DatabaseConfig) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=db_config.db_login,
            password=db_config.db_password,
            host=db_config.db_host,
            port=db_config.db_port,
            database=db_config.db_name,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session: AsyncSession = self.__session_factory()
        try:
            yield session
        except Exception:
            logger.exception(".....")
            await session.rollback()
            raise
        finally:
            await session.close()
