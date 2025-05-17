import os
from dataclasses import dataclass
from functools import cache as _cache
from typing import Self

from pydantic import Field
from pydantic_settings import BaseSettings


@dataclass
class DatabaseConfig:
    db_login: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    echo: bool
    pool_size: int

    @classmethod
    @_cache
    def provide(cls) -> Self:
        return cls(
            db_login=os.environ["POSTGRES_USER"],
            db_password=os.environ["POSTGRES_PASSWORD"],
            db_host=os.environ["POSTGRES_HOST"],
            db_port=int(os.environ["POSTGRES_PORT"]),
            db_name=os.environ["POSTGRES_DB"],
            echo=False,
            pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", 10)),
        )


class RedisSettings(BaseSettings):
    host: str = Field(env="REDIS_HOST")
    port: int = Field(env="REDIS_PORT")
    db: int = Field(env="REDIS_DB")
    password: str = Field(env="REDIS_PASSWORD")
    default_ttl: int = Field(env="REDIS_DEFAULT_TTL")

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
