from secrets import choice
from socket import gethostbyname_ex, gethostname
from uuid import UUID

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
    async with ClientSession() as session:
        async with session.get(f"{CONSUL_URL}/v1/health/service/{service_name}?passing=true") as resp:
            if resp.status != 200:
                raise HTTPException(resp.status, await resp.text())

            healthy = await resp.json(content_type=resp.content_type)

            if not healthy:
                msg = f"No healthy services found with name: {service_name}"
                raise HTTPException(msg)

            if settings.neu.devMode:
                for service in healthy:
                    if "dev" in service["Service"]["ID"]:
                        return service["Service"]

                msg = "In dev mode there should all required services should also run in dev mode"
                raise RuntimeError(msg)

            return choice(healthy)["Service"]


async def register_service(
    service_id: UUID,
    service_name: str,
    check_endpoint: str = "/ping",
    interval: str = "30s",
    tags: list[str] = [],
) -> bool:
    host = gethostbyname_ex(gethostname())[0] if settings.neu.service.host == "0.0.0.0" else settings.neu.service.host

    data = {
        "ID": service_id.hex if not settings.neu.devMode else f"{service_id.hex}_dev",
        "Name": service_name,
        "Tags": tags,
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


async def deregister_service(service_id: UUID, namespace: str = "", partition: str = "") -> str:
    service = service_id.hex if not settings.neu.devMode else f"{service_id.hex}_dev"
    data = {"ns": namespace, "partition": partition}

    async with ClientSession() as session:
        async with session.put(
            f"{CONSUL_URL}/v1/agent/service/deregister/{service}",
            json=data,
        ) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise HTTPException(resp.status, data)
            return data
