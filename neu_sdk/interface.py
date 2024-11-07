from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

from __init__ import __version__
from aredis_om import Migrator
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from neu_sdk.config import settings
from neu_sdk.registry import deregister_service, register_service


def create_app():
    service_id = uuid4()

    @asynccontextmanager
    async def lifespan(app):
        assert await register_service(
            service_id=service_id, service_name=settings.neu.service.name, tags=settings.neu.service.tags
        )
        await Migrator().run()
        yield
        await deregister_service(service_id=service_id)

    app = FastAPI(
        title=settings.neu.service.name,
        docs_url=(settings.neu.service.docs.url if settings.neu.service.docs.enable else None),
        redoc_url=None,
        version=__version__,
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
                "service_name": settings.neu.service.name,
                "version": __version__,
                "timestamp": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            }
        )

    # TODO config endpoinds

    # @app.post("/cleanup", response_class=Response)
    # async def cleanup() -> Response:
    #     #TODO
    #     return Response("To be implemented on each microservice")

    return app
