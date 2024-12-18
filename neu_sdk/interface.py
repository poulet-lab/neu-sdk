from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from json import loads
from uuid import uuid4

from aredis_om import Migrator
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

from neu_sdk import __version__
from neu_sdk.config import LOGGER, settings
from neu_sdk.registry import deregister_service, register_service
from neu_sdk.schemas import UI


def create_app(
    service_name: str,
    app_version: str,
    schema_version: str,
    tags: list[str] = [],
    lifespan_before: list[Callable] = [],
    lifespan_after: list[Callable] = [],
):
    service_id = uuid4()

    @asynccontextmanager
    async def lifespan(app):
        await Migrator().run()

        for f in lifespan_before:
            if callable(f):
                await f()
            else:
                await f

        if not settings.consul.external:
            assert await register_service(service_id=service_id, service_name=service_name, tags=tags)

        if settings.neu.devMode:
            LOGGER.warning("You are working on developer mode")
        yield
        if not settings.consul.external:
            await deregister_service(service_id=service_id)

        for f in lifespan_after:
            if callable(f):
                await f()
            else:
                await f

    app = FastAPI(
        debug=settings.neu.devMode,
        title=service_name,
        docs_url=(settings.neu.service.docs.url if settings.neu.service.docs.enable else None),
        redoc_url=None,
        version=app_version,
        license_info={
            "name": "GNU Affero General Public License v3.0 or later",
            "identifier": "AGPL-3.0-or-later",
            "url": "https://www.gnu.org/licenses/agpl-3.0.txt",
        },
        lifespan=lifespan,
    )

    @app.get("/ping", response_class=JSONResponse)
    def ping() -> JSONResponse:
        return JSONResponse(
            {
                "service_id": service_id.hex,
                "service_name": service_name,
                "app_version": app_version,
                "schema_version": schema_version,
                "sdk_version": __version__,
                "timestamp": datetime.now(UTC).strftime("%m/%d/%y %H:%M:%S"),
            }
        )

    @app.get("/schema", response_class=JSONResponse)
    def schema() -> JSONResponse:
        with open(settings.neu.ui.path, "rb") as schema:
            ui_schema = loads(schema.read())
            if "version" not in ui_schema:
                raise AttributeError("version must be defined in UI schema")

            if ui_schema["version"] == "v1":
                ui_schema = UI.model_validate(ui_schema)
            else:
                raise AttributeError("current available versions: [v1]")

        return JSONResponse(ui_schema.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True))

    # TODO config endpoinds

    # @app.post("/cleanup", response_class=Response)
    # async def cleanup() -> Response:
    #     #TODO
    #     return Response("To be implemented on each microservice")

    return app
