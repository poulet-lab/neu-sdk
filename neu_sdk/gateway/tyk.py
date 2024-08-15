from socket import gethostname
from aiohttp import ClientSession
from fastapi import HTTPException
from neu_sdk.config import settings

host = (
        gethostname()
        if settings.neu.service.host == "0.0.0.0"
        else settings.neu.service.host
    )

def keyless_conf(service_id):
    return {
        "name": f"{service_id}",
        "api_id": f"{service_id}",
        "org_id": "neu",
        "definition": {"location": "header", "key": "version"},
        "use_keyless": True,
        "version_data": {
            "not_versioned": True,
            "versions": {
                "Default": {"name": "Default","use_extended_paths": True}
            },
        },
        "proxy": {
            "listen_path": f"/api/{service_id.split("-")[-1]}/",
            "target_url": f"http://{host}:{settings.neu.service.port}",
            "strip_listen_path": True,
        },
        "enable_batch_request_support": True,
    }
async def add_to_gateway(service_id: str, auth: str= "keyless"):
    if auth == "keyless":
        data = keyless_conf(service_id)
    else:
        raise NotImplemented("Auth not yes implemented")

    async with ClientSession() as session:
        async with session.post(
            f"http://{settings.tyk.host}:{settings.tyk.port}/tyk/apis",
            headers={"x-tyk-authorization": settings.tyk.secret},
            json=data,
        ) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise HTTPException(resp.status, data)

        async with session.get(
            f"http://{settings.tyk.host}:{settings.tyk.port}/tyk/reload",
            headers={"x-tyk-authorization": settings.tyk.secret},
        ) as resp:
            if resp.status != 200:
                raise HTTPException(resp.status, await resp.text())

        return data
