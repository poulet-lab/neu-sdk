from typing import Literal
from pydantic import BaseModel, Field, field_serializer


class InterfaceOptions(BaseModel):
    name: str = Field(description="Name of the Neu service")
    app_version: str = Field(description="Version of the Neu service")
    schema_version: str = Field(description="Version of the Neu service DB schemas")
    context: Literal[
        "backend",
        "frontend",
    ] = Field("backend", description="Most probably always backend")
    ui: bool = Field(False, description="Whether it has UI schema")
    tags: list[str] = Field([], description="Additional tags")

    @property
    def service_name(self) -> str:
        return f"neu-{self.name}"

    @field_serializer("*", when_used="always")
    def serialize_to_string(value):
        return str(value)
