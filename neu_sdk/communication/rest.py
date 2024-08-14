from aiohttp.typedefs import LooseHeaders
from aiohttp import ClientSession, ClientResponse


async def get(url, headers: LooseHeaders | None = None) -> ClientResponse:
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return resp
