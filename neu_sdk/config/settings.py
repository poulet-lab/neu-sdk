from typing import Literal

from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Redis(BaseModel):
    host: str = Field("localhost")
    port: int = Field(6379)
    database: int = Field(0)
    username: str | None = Field(None)
    password: str | None = Field(None)


class Consul(BaseModel):
    host: str = Field("localhost")
    port: int = Field(8500)
    dns: int = Field(8600)


class Docs(BaseModel):
    enable: bool = Field(False)
    url: str = Field("/")


class Service(BaseModel):
    name: str = Field("")
    tags: list[str] = Field([])
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    docs: Docs = Docs()


class Neu(BaseModel):
    service: Service = Service()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    neu: Neu = Neu()
    consul: Consul = Consul()
    redis: Redis = Redis()

    log_level: Literal["critical", "error", "warning", "info", "debug"] = Field(
        "warning"
    )


settings = Settings()

REDIS_URL = "redis://"
if settings.redis.username:
    REDIS_URL += settings.redis.username
if settings.redis.password:
    REDIS_URL += ":" + settings.redis.password
if settings.redis.username or settings.redis.password:
    REDIS_URL += "@"
REDIS_URL += f"{settings.redis.host}:{settings.redis.port}/{settings.redis.database}"
