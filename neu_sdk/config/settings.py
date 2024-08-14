from typing import Literal
from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Docs(BaseModel):
    enable: bool = Field(True)
    url: str = Field("/docs")


class Service(BaseModel):
    name: str = Field("")
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    root_path: str = Field("")
    docs: Docs = Docs()


class Consul(BaseModel):
    host: str = Field("127.0.0.1")
    port: int = Field(8500)


# class Cors(BaseModel):
#     enable: bool = Field(False)
#     allow_origins: tuple[str] = Field(("*",))
#     allow_credentials: bool = Field(True)
#     allow_methods: tuple[str] = Field(("*",))
#     allow_headers: tuple[str] = Field(("*",))


# class JWT(BaseModel):
#     key: str = Field("")
#     algorithm: str = Field("HS256")
#     expiration: int = Field(10)


# class Authorization(BaseModel):
#     enable: bool = "True"
#     jwt: JWT = JWT()
#     cors: Cors = Cors()
#     token_url: str = "auth/login"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="neu_",
        env_nested_delimiter="_",
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    service: Service = Service()
    dependencies: list = Field([], description="Other service dependencies")

    consul: Consul = Consul()
    redis_url: str = Field("redis://localhost:6379/0")

    # authorization: Authorization = Authorization()

    log_level: Literal[
        "critical",
        "error",
        "warning",
        "info",
        "debug",
    ] = Field("warning")


settings = Settings()
