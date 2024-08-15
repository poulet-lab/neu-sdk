from sys import _getframe
from aiohttp.typedefs import LooseHeaders
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp import ClientSession, ClientResponse, TCPConnector
from aiohttp.resolver import AsyncResolver
from fastapi import HTTPException
from neu_sdk.config import LOGGER, settings

connector = TCPConnector(
    resolver=AsyncResolver(
        nameservers=[f"{settings.consul.host}:{settings.consul.dns}"]
    )
)


async def get_by_pk(
    service_id: str, pk: str, headers: LooseHeaders | None = None
) -> ClientResponse:
    try:
        async with ClientSession(connector=connector) as session:
            async with session.get(
                f"http://{service_id}.service.consul/{pk}", headers=headers
            ) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(404, data["detail"])
                return data
    except ClientConnectorError as e:
        LOGGER.error(
            f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}"
        )
        raise HTTPException(500, "Internal Server Error")
    except Exception as e:
        LOGGER.error(
            f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}"
        )
        raise e
