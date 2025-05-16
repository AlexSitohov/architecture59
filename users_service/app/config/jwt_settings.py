from pydantic import Field
from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(env="ALGORITHM")
    token_ttl: int = Field(env="ACCESS_TOKEN_EXPIRE_MINUTES")
