from __init__ import __version__
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from aredis_om import Migrator

from neu_sdk.registry import register_service
from neu_sdk.config import settings


def create_app(service_id: str, tags: list = []):
    # TODO maybe dependencies
    if not settings.service.name:
        settings.service.name = service_id

    async def lifespan(app):
        await register_service(service_id=service_id, tags=tags)
        await Migrator().run()
        yield

    app = FastAPI(
        title=settings.service.name,
        docs_url=settings.service.docs.url if settings.service.docs.enable else None,
        redoc_url=None,
        version=__version__,
        license_info={
            "name": "GNU Affero General Public License v3.0 or later",
            "identifier": "AGPL-3.0-or-later",
            "url": "https://www.gnu.org/licenses/agpl-3.0.txt",
        },
        lifespan=lifespan,
    )

    @app.get("/ping")
    def ping():
        return JSONResponse(
            {
                "service_id": service_id,
                "service_name": settings.service.name,
                "version": __version__,
                "timestamp": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            }
        )

    return app
