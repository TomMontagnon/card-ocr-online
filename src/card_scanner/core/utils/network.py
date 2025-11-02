import httpx


def request_url(url: str, headers=None, params=None, timeout: int = 15):
    with httpx.Client(
        http2=True, headers=headers, params=params, timeout=timeout
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp


async def request_url_async(url: str, headers=None, params=None, timeout: float = 15.0):
    async with httpx.AsyncClient(
        http2=True, headers=headers, params=params, timeout=timeout
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp
