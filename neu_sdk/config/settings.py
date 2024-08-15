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


class Tyk(BaseModel):
    host: str = Field("localhost")
    port: int = Field(8080)
    secret: str = Field("tyk")


class Consul(BaseModel):
    host: str = Field("localhost")
    port: int = Field(8500)
    dns: int = Field(8600)


class Docs(BaseModel):
    enable: bool = Field(False)
    url: str = Field("/")


class Service(BaseModel):
    name: str = Field("")
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    docs: Docs = Docs()


class Cors(BaseModel):
    enable: bool = Field(False)
    allow_origins: tuple[str] = Field(("*",))
    allow_credentials: bool = Field(True)
    allow_methods: tuple[str] = Field(("*",))
    allow_headers: tuple[str] = Field(("*",))


class JWT(BaseModel):
    key: str = Field("")
    algorithm: str = Field("HS256")
    expiration: int = Field(10)


class Authorization(BaseModel):
    enable: bool = "True"
    jwt: JWT = JWT()
    cors: Cors = Cors()
    token_url: str = "auth/login"


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
    tyk: Tyk = Tyk()
    consul: Consul = Consul()
    redis: Redis = Redis()

    authorization: Authorization = Authorization()

    log_level: Literal[
        "critical",
        "error",
        "warning",
        "info",
        "debug",
    ] = Field("warning")


settings = Settings()

REDIS_URL = "redis://"
if settings.redis.username:
    REDIS_URL += settings.redis.username
if settings.redis.password:
    REDIS_URL += ":" + settings.redis.password
if settings.redis.username or settings.redis.password:
    REDIS_URL += "@"
REDIS_URL += f"{settings.redis.host}:{settings.redis.port}/{settings.redis.database}"
