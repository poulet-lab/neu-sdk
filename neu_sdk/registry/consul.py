from socket import gethostname
from aiohttp import ClientSession
from neu_sdk.config.settings import settings


async def ping_consul() -> str:
    async with ClientSession() as session:
        async with session.get(
            f"http://{settings.consul.host}:{settings.consul.port}/v1/status/peers"
        ) as resp:
            assert resp.status == 200
            return await resp.text()


async def check_service(name: str = settings.service.name) -> dict:
    async with ClientSession() as session:
        async with session.get(
            f"http://{settings.consul.host}:{settings.consul.port}/v1/agent/service/{name}"
        ) as resp:
            assert resp.status == 200
            return await resp.text()


async def register_service(
    check_endpoint: str = "/ping", interval: str = "10s", tags: list[str] = []
) -> dict:
    url = f"http://{settings.consul.host}:{settings.consul.port}/v1/agent/service/register"

    host = (
        gethostname() if settings.service.host == "0.0.0.0" else settings.service.host
    )

    data = {
        "Name": settings.service.name,
        "Tags": tags,
        "Address": host,
        "Port": settings.service.port,
        "Check": {
            "http": f"http://{host}:{settings.service.port}{check_endpoint}",
            "interval": interval,
        },
    }

    async with ClientSession() as session:
        async with session.put(url, json=data) as resp:
            assert resp.status == 200
            return await resp.text()
