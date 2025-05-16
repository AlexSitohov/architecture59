import json
import os
from dataclasses import dataclass
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


@dataclass
class ServiceConfig:
    base_url: str
    prefix: str
    health_check: str
    public_endpoints: list[str] = None


@dataclass
class ServicesConfig:
    currency_service: ServiceConfig
    users_service: ServiceConfig

    @classmethod
    def from_json_file(cls, file_path: str):
        config_path = Path(file_path)
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls(
            currency_service=ServiceConfig(**data["currency_service"]),
            users_service=ServiceConfig(**data["users_service"]),
        )

    def get_service_config(self, service: str) -> ServiceConfig | None:
        service = service.lower()
        if service == "currency_service":
            return self.currency_service
        if service == "users_service":
            return self.users_service
        return None


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    host: str = Field(default="redis", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: str = Field(default="", env="REDIS_PASSWORD")
    default_ttl: int = Field(default=3600, env="REDIS_DEFAULT_TTL")

    @property
    def url(self) -> str:
        """Get Redis connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
