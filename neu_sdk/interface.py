from __init__ import __version__
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from aredis_om import Migrator

from neu_sdk.registry import register_service, ping_consul, check_service
from neu_sdk.config import settings, LOGGER


def create_app():
    async def lifespan(app):
        try:
            await ping_consul()
        except Exception as e:
            raise RuntimeError("Could not connect to consul")
        try:
            await register_service(
                check_endpoint=f"{settings.service.root_path}/ping",
                tags=["neu", "microservice", "breeding"],
            )
        except Exception as e:
            raise e

        for service in settings.dependencies:
            try:
                await check_service(service)
            except Exception as e:
                LOGGER.warning(
                    f"Dependent service {service} not found some functions will not work"
                )

        await Migrator().run()

        yield

    app = FastAPI(
        title=settings.service.name,
        root_path=settings.service.root_path,
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
                "service_name": settings.service.name,
                "timestamp": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            }
        )

    return app
