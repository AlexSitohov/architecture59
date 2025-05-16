import os
from dataclasses import dataclass
from functools import cache as _cache
from typing import Self


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
