from asyncio.exceptions import TimeoutError as AsyncioTimeoutError

from aiohttp import ClientConnectorError, ClientSession, ClientTimeout

from src.config import settings


async def check_website_exist(url: str) -> tuple[bool, str]:
    timeout = ClientTimeout(total=2.0)
    try:
        async with ClientSession(timeout=timeout, trust_env=True) as session:
            async with session.get(url, allow_redirects=False, ssl=False) as response:
                if response.status < 400:
                    return True, "Status code < 400"
                return False, "Status code >= 400"
    except AsyncioTimeoutError:
        return False, "TimeoutError"
    except ClientConnectorError:
        return False, "ClientConnectorError"


def get_short_url(url_token: str):
    return f"http://{settings.APP_HOST}:{settings.APP_PORT}/{url_token}"
