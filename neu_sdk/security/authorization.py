from datetime import datetime, timedelta, timezone
from re import match
from sys import _getframe
from typing import Literal

from bcrypt import checkpw, gensalt, hashpw
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, Field

from neu_sdk.config import LOGGER
from neu_sdk.config.settings import settings

KIND = {"session": 0, "api": 1}
SALT = gensalt()


class Payload(BaseModel):
    sub: int
    token_kind: int
    exp: datetime | None = Field(None)


class Token(BaseModel):
    access_token: str = Field()
    token_type: Literal["bearer"] = Field("bearer")


def password_strength(password):
    if not match(
        r"^.*(?=.{8})(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@£$%^&*()_+={}?:~\[\]])[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$",
        password,
    ):
        raise ValueError(
            "Password must be at least 8 characters long and include at least one number, one lowercase letter, one uppercase letter, and one special character."
        )
    return True


def encrypt_password(password: str) -> str:
    return hashpw(password.encode(), SALT).decode()


def check_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode(), hashed_password.encode())


async def create_token(
    user_id: int,
    expiration: int | None = None,
    token_kind: Literal["api", "session"] = "session",
) -> str:
    try:
        payload = Payload(
            sub=user_id,
            token_kind=KIND[token_kind],
            exp=(
                datetime.now(timezone.utc) + timedelta(minutes=expiration)
                if expiration
                else None
            ),
        )
        token = Token(
            access_token=encode(
                payload.model_dump(exclude_none=True, exclude_unset=True),
                settings.authorization.jwt.key,
                algorithm=settings.authorization.jwt.algorithm,
            )
        )

    except Exception as e:
        LOGGER.info(f"neu_sdk.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise HTTPException(400, "There was an error creating the token")

    return token


async def validate_token(
    token: str | None = Depends(HTTPBearer if settings.authorization.enable else None),
) -> Payload:
    if token is not None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = decode(
                token,
                settings.authorization.jwt.key,
                algorithms=[settings.authorization.jwt.algorithm],
            )
            payload = Payload(**payload)
            if payload.exp:
                if payload.exp - datetime.now(timezone.utc) < timedelta():
                    raise credentials_exception

        except InvalidTokenError as e:
            raise credentials_exception from e

        return payload
