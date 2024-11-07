from sys import _getframe
from typing import Any, Literal

from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.typedefs import LooseHeaders, Query
from fastapi import HTTPException

from neu_sdk.config import LOGGER, settings
from neu_sdk.registry import get_service

# TODO grpc maybe


async def request(
    service_name: str,
    *,
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET",
    scheme: Literal["http", "https"] = "http",
    path: str = "/",
    params: Query = {},
    headers: LooseHeaders | None = None,
    data: dict[str, Any] = {},
) -> dict:
    try:
        service = await get_service(service_name)

        async with ClientSession() as session:
            _s = (
                session.get
                if method == "GET"
                else (
                    session.post
                    if method == "POST"
                    else (
                        session.put
                        if method == "PUT"
                        else (session.patch if method == "PATCH" else session.delete if method == "DELETE" else None)
                    )
                )
            )
            if _s is None:
                raise HTTPException(f"Unsupported method: {method}")

            async with _s(
                f"{scheme}://{service['Address']}:{service['Port']}{path}", params=params, headers=headers, json=data
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(resp.status, await resp.text())
                return await resp.json(content_type=resp.content_type)
    except ClientConnectorError as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise HTTPException(500, "Internal Server Error")
    except Exception as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise e


async def get_by_pk(service_name: str, pk: str, headers: LooseHeaders | None = None) -> ClientResponse:
    data = await get_service(service_name)
    try:
        async with ClientSession() as session:
            async with session.get(f"http://{data['Address']}:{data['Port']}/{pk}", headers=headers) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(resp.status, data["detail"])
                return data
    except ClientConnectorError as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise HTTPException(500, "Internal Server Error")
    except Exception as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise e


async def delete_by_pk(service_name: str, pk: str, headers: LooseHeaders | None = None) -> ClientResponse:
    data = await get_service(service_name)
    try:
        async with ClientSession() as session:
            async with session.delete(f"http://{data['Address']}:{data['Port']}/{pk}", headers=headers) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(resp.status, data["detail"])
                return data
    except ClientConnectorError as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise HTTPException(500, "Internal Server Error")
    except Exception as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise e


async def trigger_cleanup(service_name: str, headers: LooseHeaders | None = None) -> ClientResponse:
    data = await get_service(service_name)
    try:
        async with ClientSession() as session:
            async with session.delete(f"http://{data['Address']}:{data['Port']}/cleanup", headers=headers) as resp:
                data = await resp.json(content_type=resp.content_type)
                if resp.status != 200:
                    raise HTTPException(resp.status, data["detail"])
                return data
    except ClientConnectorError as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise HTTPException(500, "Internal Server Error")
    except Exception as e:
        LOGGER.error(f"{settings.neu.service.name}.{__name__}.{_getframe().f_code.co_name}: {e}")
        raise e
