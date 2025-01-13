from pydantic import BaseModel, Field


class InterfaceOptions(BaseModel):
    name: str = Field(description="Name of the Neu service")
    app_version: str = Field(description="Version of the Neu service")
    schema_version: str = Field(description="Version of the Neu service DB schemas")
    ui: bool = Field(False, description="Whether it has UI schema")
    tags: list[str] | None = Field(None, description="Additional tags")

    @property
    def service_name(self) -> str:
        return f"neu-{self.name}"

    @property
    def consul_tags(self) -> list[str]:
        tags = ["neu", f"name:{self.name}", "api"]
        if self.ui:
            tags += ["ui"]
        if self.tags:
            tags += self.tags

        return tags
