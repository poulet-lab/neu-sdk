from enum import Enum

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
    type: FieldTypes = Field("string", description="Type of the field")
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


class DetailPage(BaseModel):
    components: list[Component] = []


class OverviewPage(BaseModel):
    pass


class Pages(BaseModel):
    overview_page: OverviewPage | None = Field(
        None, description="Some services might not need an overview page"
    )
    detail_page: DetailPage = DetailPage()


class Request(BaseModel):
    service_name: str = Field(description="Neu service to make a request")
    route: str = Field(description="Neu service route")
    method: Methods = Field("GET", description="Request method")
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


class Options(BaseModel):
    sidebar: bool = Field(
        False, description="Whether to show the service on the sidebar"
    )


class UI(BaseModel):
    options: Options = Options()
    definitions: Definitions = Definitions()
    pages: Pages = Pages()
