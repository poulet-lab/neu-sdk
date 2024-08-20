from sys import _getframe
from aiohttp.typedefs import LooseHeaders
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp import ClientSession, ClientResponse
from fastapi import HTTPException
from neu_sdk.config import LOGGER, settings
from neu_sdk.registry import get_service

# TODO use consul dns
# TODO grpc maybe


async def get_by_pk(
    service_id: str, pk: str, headers: LooseHeaders | None = None
) -> ClientResponse:
    data = await get_service(service_id)
    try:
        async with ClientSession() as session:
            async with session.get(
                f"http://{data['Address']}:{data['Port']}/{pk}", headers=headers
            ) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(resp.status, data["detail"])
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


async def delete_by_pk(
    service_id: str, pk: str, headers: LooseHeaders | None = None
) -> ClientResponse:
    data = await get_service(service_id)
    try:
        async with ClientSession() as session:
            async with session.delete(
                f"http://{data['Address']}:{data['Port']}/{pk}", headers=headers
            ) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(resp.status, data["detail"])
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


async def trigger_cleanup(
    service_id: str, headers: LooseHeaders | None = None
) -> ClientResponse:
    data = await get_service(service_id)
    try:
        async with ClientSession() as session:
            async with session.delete(
                f"http://{data['Address']}:{data['Port']}/cleanup", headers=headers
            ) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(resp.status, data["detail"])
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
