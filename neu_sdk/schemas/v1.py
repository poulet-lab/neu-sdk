from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class FieldTypes(str, Enum):
    STRING = "string"
    NUMBER = "number"
    EMAIL = "email"
    USERNAME = "username"
    PASSWORD = "password"
    JSON = "json"
    ARRAY = "array"


class ComponentTypes(str, Enum):
    HEADER = "header"
    ORDERED_BOX = "ordered_box"
    CONTAINER = "container"
    TAB = "tab"
    TABLE = "table"
    MODAL = "modal"
    JSON = "json"


class ModuleTypes(str, Enum):
    SIDEBAR = "sidebar"
    HEADER = "header"
    MAIN = "main"
    SECONDARY = "secondary"


class Functions(str, Enum):
    CREATE = "create"
    UPDATE = "update"


class Methods(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


class FieldOptions(BaseModel):
    api_name: str | None = Field(
        None, description="Rename the field to avoid duplicates"
    )
    display_name: str | None = Field(None, description="The name to render on UI.")
    type: FieldTypes = Field(FieldTypes.STRING, description="Type of the field")
    required: bool = Field(False, description="Whether it is mandatory on create")
    dangerous: bool = Field(
        False, description="Whether extra care should be taken for this field"
    )


class Component(BaseModel):
    name: str = Field(
        description="unique name for the component, will be used as id in UI"
    )
    type: ComponentTypes = Field(description="type of the component to use in UI")
    title: str | None = Field(None, description="Title of the component to use in UI")
    href: str | None = Field(
        None, description="Whether to redirect by clicking on the component title"
    )
    fields: list[str] | None = Field(None, description="Field names to display")

    components: list["Component"] | None = Field(
        [], description="use for container type"
    )


class Sidebar(BaseModel):
    components: list[Component] = []


class Header(BaseModel):
    components: list[Component] = []


class Main(BaseModel):
    components: list[Component] = []


class Secondary(BaseModel):
    components: list[Component] = []


class Page(BaseModel):
    path: str = Field(description="Page path")
    modules: dict[ModuleTypes, list[Component]]


class Request(BaseModel):
    service_name: str = Field(description="Neu service to make a request")
    route: str = Field(description="Neu service route")
    method: Methods = Field(Methods.GET, description="Request method")
    is_list: bool = Field(
        False, description="Whether the returned data are in a form of list"
    )
    fields: dict[str, FieldOptions]


class FunctionOptions(BaseModel):
    fields: list[str] = Field([], description="the fields to use in the function")


class Definitions(BaseModel):
    request: dict[str, Request] = Field({}, description="All the available fields")
    functions: dict[Functions, FunctionOptions] = Field(
        {}, description="options of pre-defined functions"
    )


class UI(BaseModel):
    version: Literal["v1"] = Field(description="neu ui schema version")
    definitions: Definitions = Definitions()
    pages: list[Page] = Field(description="list of pages for the service")
