from re import sub
from __init__ import __version__
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from aredis_om import Migrator

from neu_sdk.gateway import add_to_gateway
from neu_sdk.registry import register_service
from neu_sdk.config import settings


def create_app(service_id: str, tags: list = []):
    if not settings.neu.service.name:
        settings.neu.service.name = service_id

    async def lifespan(app):
        await register_service(service_id=service_id, tags=tags)
        await add_to_gateway(service_id=service_id)
        await Migrator().run()
        yield

    endpoint = service_id.replace("neu-", "")
    endpoint = sub("[-_]", "/", endpoint)
    endpoint = f"/api/{endpoint}"

    app = FastAPI(
        title=settings.neu.service.name,
        docs_url=(
            settings.neu.service.docs.url if settings.neu.service.docs.enable else None
        ),
        redoc_url=None,
        version=__version__,
        license_info={
            "name": "GNU Affero General Public License v3.0 or later",
            "identifier": "AGPL-3.0-or-later",
            "url": "https://www.gnu.org/licenses/agpl-3.0.txt",
        },
        lifespan=lifespan,
        root_path=endpoint,
    )

    @app.get("/ping")
    def ping():
        return JSONResponse(
            {
                "service_id": service_id,
                "service_name": settings.neu.service.name,
                "version": __version__,
                "timestamp": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            }
        )

    return app
