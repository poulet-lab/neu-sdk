from aiohttp import ClientSession
from fastapi import HTTPException
from neu_sdk.config import settings


async def add_keyless(service_id: str):
    data = {
        "name": f"{service_id}",
        "api_id": f"{service_id}",
        "org_id": "neu",
        "definition": {"location": "header", "key": "version"},
        "use_keyless": True,
        "version_data": {
            "not_versioned": True,
            "versions": {"Default": {"name": "Default"}},
        },
        "proxy": {
            "service_discovery": {
                "use_discovery_service": True,
                "query_endpoint": f"http://{settings.consul.host}:{settings.consul.port}/v1/agent/service/{service_id}",
                "data_path": "Address",
                "port_data_path": "Port",
                "target_path": f"{service_id.rsplit("-")[-1]}",
                "cache_disabled": True,
                "cache_timeout": 60,
            }
        },
    }

    async with ClientSession() as session:
        async with session.post(
            f"http://{settings.tyk.host}:{settings.tyk.port}/tyk/apis",
            headers={"x-tyk-authorization": settings.tyk.secret},
            json=data,
        ) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise HTTPException(resp.status, data)
            return data
