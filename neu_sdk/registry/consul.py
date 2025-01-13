from secrets import choice
from socket import gethostbyname_ex, gethostname
from ulid import ULID

from aiohttp import ClientSession
from fastapi import HTTPException

from neu_sdk.config.settings import settings

CONSUL_URL = f"http://{settings.consul.host}:{settings.consul.port}"


async def ping_consul():
    async with ClientSession() as session:
        async with session.get(f"{CONSUL_URL}/v1/status/peers") as resp:
            if resp.status != 200:
                raise HTTPException(resp.status, await resp.text())


async def get_service(service_name: str) -> dict:
    params = {"passing": "true"}
    if settings.neu.devMode:
        params["filter"] = '"dev" in Service.Tags'
    async with ClientSession() as session:
        async with session.get(f"{CONSUL_URL}/v1/health/service/{service_name}", params=params) as resp:
            if resp.status != 200:
                raise HTTPException(resp.status, await resp.text())

            healthy = await resp.json(content_type=resp.content_type)

            if not healthy:
                msg = f"Service: {service_name} is unavailable"
                raise HTTPException(503, msg)

            return choice(healthy)["Service"]


async def register_service(
    service_id: ULID,
    service_name: str,
    check_endpoint: str = "/ping",
    interval: str = "30s",
    tags: list[str] = [],
    meta: dict[str, str] = {},
) -> bool:
    host = gethostbyname_ex(gethostname())[0] if settings.neu.service.host == "0.0.0.0" else settings.neu.service.host

    if settings.neu.devMode:
        tags += ["dev"]

    meta["app"] = "neu"

    data = {
        "ID": str(service_id),
        "Name": service_name,
        "Tags": tags,
        "Meta": meta,
        "Address": host,
        "Port": settings.neu.service.port,
        "Check": {
            "http": f"http://{host}:{settings.neu.service.port}{check_endpoint}",
            "interval": interval,
        },
    }

    async with ClientSession() as session:
        async with session.put(f"{CONSUL_URL}/v1/agent/service/register", json=data) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise HTTPException(resp.status, data)
            return True


async def deregister_service(service_id: ULID, namespace: str = "", partition: str = "") -> str:
    data = {"ns": namespace, "partition": partition}

    async with ClientSession() as session:
        async with session.put(
            f"{CONSUL_URL}/v1/agent/service/deregister/{service_id!s}",
            json=data,
        ) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise HTTPException(resp.status, data)
            return data
