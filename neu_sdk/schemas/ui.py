from ast import main
from email import header
from enum import Enum
from typing import Literal

from httpx import request
from pydantic import BaseModel, Field as PydanticField


class FieldTypes(str, Enum):
    STRING = "string"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    JSON = "json"
    ARRAY = "array"


class ComponentTypes(str, Enum):
    HEADER = "header"
    LIST = "list"
    PLAIN = "plain"


class SectionTypes(str, Enum):
    SIDEBAR = "sidebar"
    HEADER = "header"
    MAIN = "main"
    SECONDARY = "secondary"


class SectionTypes(str, Enum):
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


class Field(BaseModel):
    label: str | None = PydanticField(None, description="The name to render on UI.")
    type: FieldTypes = PydanticField(FieldTypes.STRING, description="Type of the field")
    required: bool = PydanticField(False, description="Whether it is mandatory on create")


class Element(BaseModel):
    request: str = PydanticField(description="reference to a request to use in the element")


class Component(BaseModel):
    key: str = PydanticField(description="unique name for the component, will be used as id in UI")
    type: ComponentTypes = PydanticField(description="type of the component to use in UI")
    title: str | None = PydanticField(None, description="Title of the component to use in UI")
    href: str | None = PydanticField(None, description="Whether to redirect by clicking on the component title")
    request: str = PydanticField(description="reference to a request to use in the component")
    elements: dict[str, Element] = PydanticField(
        {}, description="elements to render in the component, key is the available element name"
    )
    components: list["Component"] | None = PydanticField([], description="use for container type")


class Sidebar(BaseModel):
    components: list[Component] = []


class Header(BaseModel):
    components: list[Component] = []


class Main(BaseModel):
    components: list[Component] = []


class Secondary(BaseModel):
    components: list[Component] = []


class Section(BaseModel):
    header: Header = Header()
    main: Main = Main()
    secondary: Secondary = Secondary()
    sidebar: Sidebar = Sidebar()


class Page(BaseModel):
    section: Section = Section()


class Request(BaseModel):
    service_name: str = PydanticField(description="Neu service to make a request")
    path: str = PydanticField(description="Neu service route")
    method: Methods = PydanticField(Methods.GET, description="Request method")
    fields: dict[str, Field] = PydanticField({}, description="Request fields, key is the field name")


class UI(BaseModel):
    version: Literal["v1"] = PydanticField(description="neu ui schema version")
    requests: dict[str, Request] = PydanticField(
        {}, description="neu ui schema requests, key is the request identifier"
    )
    pages: dict[str, Page] = PydanticField(description="dict of pages for the service, key is the path")
