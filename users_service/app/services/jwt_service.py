from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import JWTError, jwt
from typing import Optional

from starlette import status

from app.config.jwt_settings import JWTSettings


class JWTService:
    def __init__(self, jwt_config: JWTSettings):
        self.jwt_config = jwt_config

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.jwt_config.token_ttl)
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.jwt_config.key, algorithm=self.jwt_config.algorithm
        )
        return encoded_jwt

    def verify_access_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                self.jwt_config.key,
                options={"verify_signature": True},
                algorithms=[self.jwt_config.algorithm],
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token expired {e}",
            )
